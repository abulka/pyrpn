from flask import Flask, render_template, redirect, url_for, request, jsonify
from parse import parse
from rpn_exceptions import RpnError
import logging
from logger import config_log
from server_forms import ConverterForm, ExampleForm
import redis
import re
import json
from attr import attrs, attrib, evolve
from lib import cheap_redis_db
from example_model import Example
from examples_sync import ExamplesSync
import os
import settings
import sendgrid
from sendgrid.helpers.mail import *
from program import Program
from cmd_list import cmd_list

log = logging.getLogger(__name__)
config_log(log)

FORCE_ADMIN = settings.ADMIN

if os.environ.get("REDIS_URL"):
    # Heroku
    db = redis.from_url(os.environ.get("REDIS_URL"), charset="utf-8", decode_responses=True)
else:
    db = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)

cheap_redis_db.config.set_connection(db)

app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

SENDGRID_API_KEY = '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'
# app.config['SENDGRID_API_KEY'] = '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'
# app.config['SENDGRID_DEFAULT_FROM'] = 'abulka@gmail.com'
# mail = SendGrid(app)

es = ExamplesSync.create(settings.APP_DIR, settings.PRODUCTION)


@app.route('/', methods=["GET", "POST"])
@app.route('/<int:id>', methods=["GET"])
def index(id=None):
    rpn = rpn_free42 = 'Press Convert'
    parse_errors = ''
    if request.method == 'GET':
        log.info(f'main converter page viewed, example {id}')
        form = ConverterForm()
        if id:
            example = Example.get(id)
            form.source.process_data(example.source)
    elif request.method == 'POST':
        # We are asking for the source to be converted to RPN
        form = ConverterForm(request.form)
        if form.validate_on_submit():
            spy(form.source.data, form.source.default)
            try:
                program = parse(form.source.data, {'emit_pyrpn_lib': form.emit_pyrpn_lib.data})
                rpn = program.lines_to_str(comments=form.comments.data, linenos=form.line_numbers.data)
                rpn_free42 = program.lines_to_str(comments=False, linenos=True)
            except RpnError as e:
                parse_errors = str(e)
    return render_template('index.html', form=form, rpn=rpn, rpn_free42=rpn_free42, title='source code converter', parse_errors=parse_errors)

def spy(source, default_source):
    s = source.replace('\r', '')
    if s.strip() == default_source.strip():
        log.info('main converter - default demo converted.')
        return
    line = '-' * 10
    s = s.replace('\n', '|').replace('\r', '')
    s = re.sub(r"\s+", ' ', s)  # Replace all runs of whitespace with a single space
    source_trimmed = s
    source_full = f'{line}\n{source}\n{line}'
    log.info(f'main converter converting python code: {source_trimmed}\n{source_full}')


@app.route('/examples')
def examples_list():
    log.info(f'examples being listed.')
    admin = request.args.get('admin')
    tag = request.args.get('tag')
    if FORCE_ADMIN: admin = True

    if len(Example.ids()) == 0:
        es.repopulate_redis()
        # example = Example(**example_01)  # create the first example
    examples = [Example.get(id) for id in Example.ids()]
    for eg in examples:
        eg.sortnum = int(eg.sortnum)  # repair the integer
    examples_sorted = sorted(examples, key=lambda eg: (eg.sortnum, eg.filename, eg.id), reverse=True)

    all_examples, all_tags = prepare_examples_and_tags(examples_sorted)
    show_initial_tag = tag if tag else 'Introductory_Examples'
    return render_template('examples_list.html', examples=all_examples, title="Examples", admin=admin, all_tags=all_tags, show_initial_tag=show_initial_tag)


def prepare_examples_and_tags(examples):
    """
     Turn the list of example objects into a list of dicts.  Each dict has the keys
     'example' and 'tags', where tags is a poperly parsed list of tags (whereas example.tags
     is a mere comma separated string)

     Also prepares a list of (tag, tag with spaces restored) tuples in all_tags.

    :param examples: list of example objects
    :return: tuple all_examples, all_tags
    """
    all_examples = []
    all_tags = set()
    for eg in examples:
        eg_tags = [tag.strip() for tag in eg.tags.split(',') if eg.tags.strip() != '']
        all_tags = all_tags | set(eg_tags)
        eg_dict = {'example': eg,
                   'tags': eg_tags}
        all_examples.append(eg_dict)
    all_tags = sorted(all_tags)
    all_tags.remove('User_Interface')
    all_tags.insert(0, 'User_Interface')
    all_tags.remove('Introductory_Examples')
    all_tags.insert(0, 'Introductory_Examples')
    all_tags.remove('Advanced')
    all_tags.append('Advanced')
    all_tags = [(tag, tag.replace('_', ' ')) for tag in all_tags]
    return all_examples, all_tags


@app.route('/sync')
def examples_sync():
    do = request.args.get('do')
    purge = request.args.get('purge')
    if do:
        es.repopulate_redis()
        return redirect(url_for('examples_sync'))  # so that the 'do' and 'purge' are removed after each do/purge
    elif purge:
        es.purge_redis()
        return redirect(url_for('examples_sync'))
    else:
        es.build_mappings()
    return render_template('examples_sync.html', title="Example Synchronisation", infos=es.mappings, ls=es.ls(), admin=True)


@app.route('/example', methods=['GET', 'POST'])
def example_create():
    """
    Handle GET blank initial forms and POST creating new entries.
    """
    admin = request.args.get('admin')
    if FORCE_ADMIN: admin = True

    if request.method == 'POST':
        log.debug(f'example_create POST public {request.values.get("public")}')
        form = ExampleForm(request.form)
        # example = Example(**dict(request.values))  # why doesn't this work?
        if form.validate():
            example = Example(
                title=form.title.data,
                source=form.source.data,
                description=form.description.data,
                public = Example.bool_to_redis_bool(form.public.data),
                filename=form.filename.data,
                sortnum=form.sortnum.data,
                tags=form.tags.data,
            )
            log.info(f'created example {example}')
            return redirect(url_for('example_edit', id=example.id))
    else:  # GET
        form = ExampleForm()
        if not admin:
            form.tags.process_data(settings.EDITOR_USER_EXAMPLES_TAGS)
    return render_template('example.html', form=form, title='Example Edit', admin=admin, example_id='')

@app.route('/example/<int:id>', methods=['GET', 'POST'])
def example_edit(id):
    """
    Handle GET existing example and POST updating it.  Forms cannot send put verb.
    If pass param ?delete=1 then do a DELETE.  Forms cannot send delete verb.
    """
    delete = request.args.get('delete')  # Wish forms could send delete verb properly...
    clone = request.args.get('clone')
    to_rpn = request.args.get('to-rpn')
    vote = request.args.get('vote')
    admin = request.args.get('admin')
    if FORCE_ADMIN: admin = True

    example = Example.get(id)
    # log.info(f'example_edit: id {id} delete flag {delete} example is {example}')

    if request.method == 'GET' and delete:
        example.delete()
        return redirect(request.referrer)

    if request.method == 'GET' and clone:
        example_clone = evolve(example, id=None, title=example.title + ' copy', filename='', tags=settings.EDITOR_USER_EXAMPLES_TAGS, description='Enter new description here')  # hopefully will reallocate id and save it to redis
        print(example_clone)
        return redirect(url_for('example_edit', id=example_clone.id))

    if request.method == 'GET' and to_rpn:
        options = {'emit_pyrpn_lib': False}
        rpn = parse(example.source, options).lines_to_str(comments=True, linenos=True)
        rpn_free42 = parse(example.source, options).lines_to_str(comments=False, linenos=True)
        log.info(f'main converter converting example {example.id} title "{example.title}"')
        return jsonify(rpn=rpn, rpn_free42=rpn_free42)

    if request.method == 'GET' and vote:
        try:
            vote_via_email(example)
        except:
            return render_template('example_vote_thanks.html', title='Example Vote', example=example, success=False)
        else:
            return render_template('example_vote_thanks.html', title='Example Vote', example=example, success=True)

    if request.method == 'GET':
        dic = example.asdict
        dic['public'] = Example.redis_bool_to_bool(example.public)
        form = ExampleForm(**dic)
        log.debug('id %s', id)
        return render_template('example.html', form=form, title='Example Edit', admin=admin, example_id=id)

    elif request.method == 'POST':  # Wish forms could send put verb properly...
        form = ExampleForm(request.form)
        if form.validate():
            # Update
            example.title=form.title.data
            example.source=form.source.data
            example.description=form.description.data
            example.public = Example.bool_to_redis_bool(form.public.data)
            example.filename=form.filename.data
            example.sortnum=form.sortnum.data
            example.tags=form.tags.data
            example.save()
            log.info(f'example_edit: {id} updated and saved {example}')
            es.save_to_file(example)
        else:
            log.warning('form did not validate')
        return render_template('example.html', form=form, title='Example Edit', admin=admin, example_id=id)

def vote_via_email(example):
    dic = example.asdict
    for key in set(dic.keys()) - set(('title', 'description', 'source', 'sortnum')):
        del dic[key]  # don't persist this key
    dic['sortnum'] = int(dic['sortnum'])  # repair the integer
    body = json.dumps(dic, sort_keys=True, indent=4)
    # email it
    try:
        sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
        from_email = Email("pyrpn-donotreply@gmail.com")
        to_email = Email("abulka@gmail.com")
        subject = f'Vote for python rpn example \"{dic["title"]}\"'
        content = Content("text/plain", body)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        log.info(response)
    except Exception as e:
        log.exception("Couldn't send vote email")
        raise e
    else:
        log.info(f'vote for example {example.id} title {example.title} emailed, response {response.status_code}')
    log.info(body)

@app.route('/py-rpn-lib', methods=['GET'])
def py_rpn_lib():
    program = Program()
    program.rpn_templates.need_all_templates = True
    program.emit_needed_rpn_templates(as_local_labels=False)
    rpn = program.lines_to_str(comments=True, linenos=True)
    rpn_free42 = program.lines_to_str(comments=False, linenos=True)
    log.info('generating standalone RPN support lib')
    return render_template('pyrpnlib.html', rpn=rpn, rpn_free42=rpn_free42, title='PyRpn Support Lib')

@app.route('/cmds')
def cmds():
    return render_template('cmd_list.html', cmd_list=cmd_list, title='List of HP42S Commands Reference')

@app.route('/help')
def help():
    return render_template('help.html', title='Help & User Guide')

@app.route('/canvas')
def canvas():
    return render_template('canvas_primitives.html', title='Canvas for 42S Simulator')

@app.route('/subscribe')
def subscribe():
    return render_template('subscribe.html', title='Subscribe to Mailing List')

@app.route('/hello')
def hello():
    return render_template('hello.html', name='andy')

@app.route('/test')
def test():
    rpn = do()
    return f'<html><body><pre>{"hi there"}</pre></body></html>'


if __name__ == '__main__':
    # This code does not run if running via gunicorn on heroku
    app.jinja_env.auto_reload = True
    app.run(debug=True)
