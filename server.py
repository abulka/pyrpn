from flask import Flask, render_template, redirect, url_for, request, jsonify
from parse import parse
import logging
from logger import config_log
from server_forms import ConverterForm, ExampleForm
import redis
import json
from attr import attrs, attrib, evolve
from lib import cheap_redis_db
from example_model import Example
from examples_sync import ExamplesSync
import os

log = logging.getLogger(__name__)
config_log(log)

PRODUCTION = 'I_AM_ON_HEROKU' in os.environ
LOCAL = not PRODUCTION
FORCE_ADMIN = LOCAL
# FORCE_ADMIN = False

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

APP_DIR = os.path.dirname(os.path.realpath(__file__))

es = ExamplesSync.create(APP_DIR, PRODUCTION)


@app.route('/', methods=["GET", "POST"])
@app.route('/<int:id>', methods=["GET"])
def index(id=None):
    rpn = rpn_free42 = 'Press Convert'
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
            program = parse(form.source.data)
            log.info(f'main converter converting python code:\n{form.source.data}')
            rpn = program.lines_to_str(comments=form.comments.data, linenos=form.line_numbers.data)
            rpn_free42 = program.lines_to_str(comments=False, linenos=True)
    return render_template('index.html', form=form, rpn=rpn, rpn_free42=rpn_free42, title='source code converter')


def do(source, comments=True, linenos=True):
    program = parse(source)
    rpn = program.lines_to_str(comments=comments, linenos=linenos)
    return rpn


@app.route('/examples')
def examples_list():
    log.info(f'examples being listed.')
    admin = request.args.get('admin')
    if FORCE_ADMIN: admin = True

    if len(Example.ids()) == 0:
        es.repopulate_redis()
        # example = Example(**example_01)  # create the first example
    examples = [Example.get(id) for id in Example.ids()]
    for eg in examples:
        eg.sortnum = int(eg.sortnum)  # repair the integer
    examples_sorted = sorted(examples, key=lambda eg: (eg.sortnum, eg.filename, eg.id), reverse=True)
    return render_template('examples_list.html', examples=examples_sorted, title="Examples", admin=admin)


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
            )
            log.info(f'created example {example}')
            return redirect(url_for('example_edit', id=example.id))
    else:  # GET
        form = ExampleForm()
    return render_template('example.html', form=form, title='Example Edit', admin=admin)

@app.route('/example/<int:id>', methods=['GET', 'POST'])
def example_edit(id):
    """
    Handle GET existing example and POST updating it.  Forms cannot send put verb.
    If pass param ?delete=1 then do a DELETE.  Forms cannot send delete verb.
    """
    delete = request.args.get('delete')  # Wish forms could send delete verb properly...
    clone = request.args.get('clone')
    to_rpn = request.args.get('to-rpn')
    admin = request.args.get('admin')
    if FORCE_ADMIN: admin = True

    example = Example.get(id)
    # log.info(f'example_edit: id {id} delete flag {delete} example is {example}')

    if request.method == 'GET' and delete:
        example.delete()
        return redirect(request.referrer)

    if request.method == 'GET' and clone:
        example_clone = evolve(example, id=None, title=example.title + ' copy')  # hopefully will reallocate id and save it to redis
        return redirect(url_for('example_edit', id=example_clone.id))

    if request.method == 'GET' and to_rpn:
        rpn = parse(example.source).lines_to_str(comments=True, linenos=True)
        rpn_free42 = parse(example.source).lines_to_str(comments=False, linenos=True)
        return jsonify(rpn=rpn, rpn_free42=rpn_free42)

    if request.method == 'GET':
        dic = example.asdict
        dic['public'] = Example.redis_bool_to_bool(example.public)
        form = ExampleForm(**dic)
        return render_template('example.html', form=form, title='Example Edit', admin=admin)

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
            example.save()
            log.info(f'example_edit: {id} updated and saved {example}')
            es.save_to_file(example)
        else:
            log.warning('form did not validate')
        return render_template('example.html', form=form, title='Example Edit', admin=admin)

@app.route('/help')
def help():
    return render_template('help.html', title='Help & User Guide')

@app.route('/hello')
def hello():
    return render_template('hello.html', name='andy')

@app.route('/test')
def test():
    rpn = do()
    return f'<html><body><pre>{rpn}</pre></body></html>'


if __name__ == '__main__':
    # This code does not run if running via gunicorn on heroku
    app.jinja_env.auto_reload = True
    app.run(debug=True)
