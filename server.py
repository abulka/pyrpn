from flask import Flask, render_template, redirect, url_for, request, jsonify
from parse import parse
import logging
from logger import config_log
from server_forms import MyForm, ExampleForm
from examples import example_01
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
        form = MyForm()
        if id:
            example = Example.get(id)
            form.source.process_data(example.source)
    elif request.method == 'POST':
        # We are asking for the source to be converted to RPN
        form = MyForm(request.form)
        if form.validate_on_submit():
            program = parse(form.source.data)
            rpn = program.lines_to_str(comments=form.comments.data, linenos=form.line_numbers.data)
            rpn_free42 = program.lines_to_str(comments=False, linenos=True)
    return render_template('index.html', form=form, rpn=rpn, rpn_free42=rpn_free42, title='source code converter')


def do(source, comments=True, linenos=True):
    program = parse(source)
    rpn = program.lines_to_str(comments=comments, linenos=linenos)
    return rpn


@app.route('/examples')
def examples_list():
    admin = request.args.get('admin')
    if LOCAL: admin = True

    if len(Example.ids()) == 0:
        example = Example(**example_01)  # create the first example
        log.info('first example re-created', example.asdict)
        # return f'<html><body><pre>{example}</pre></body></html>'
    examples = [Example.get(id) for id in Example.ids()]
    examples_sorted = sorted(examples, key=lambda eg: eg.sortnum, reverse=True)
    return render_template('examples_list.html', examples=examples_sorted, title="Examples", admin=admin)


@app.route('/sync')
def examples_sync():
    do = request.args.get('do')
    if do:
        es.files_to_redis()
        es.redis_to_files()
    es.build_mappings()
    return render_template('examples_sync.html', title="Example Synchronisation", infos=es.mappings, ls=es.ls(), admin=True)


@app.route('/example', methods=['GET', 'POST'])
def example_create():
    """
    Handle GET blank initial forms and POST creating new entries.
    """
    admin = request.args.get('admin')
    disabled = '' if admin else 'disabled'
    if LOCAL: disabled = False

    if request.method == 'POST':
        log.debug(f'example_create POST public {request.values.get("public")}')
        form = ExampleForm(request.form)
        # example = Example(**dict(request.values))  # why doesn't this work?
        if form.validate():
            example = Example(
                title=request.values.get('title'),
                source=request.values.get('source'),
                description=request.values.get('description'),
                public = Example.bool_to_redis_bool(request.values.get('public')),
            )
            log.info(example)
            return redirect(url_for('example_edit', id=example.id))
    else:  # GET
        form = ExampleForm()
    return render_template('example.html', form=form, title='Example Edit', disabled=disabled)

@app.route('/example/<int:id>', methods=['GET', 'POST'])
def example_edit(id):
    """
    Handle GET existing example and POST updating it.  Forms cannot send put verb.
    If pass param ?delete=1 then do a DELETE.  Forms cannot send delete verb.
    """
    delete = request.args.get('delete')  # Wish forms could send delete verb properly...
    clone = request.args.get('clone')
    to_rpn = request.args.get('to-rpn')

    example = Example.get(id)
    # log.info(f'example_edit: id {id} delete flag {delete} example is {example}')

    if request.method == 'GET' and delete:
        example.delete()
        return redirect(url_for('examples_list'))  # 'url_for' takes the name of view def

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
        return render_template('example.html', form=form, title='Example Edit')

    elif request.method == 'POST':  # Wish forms could send put verb properly...
        form = ExampleForm(request.form)
        if form.validate():
            example.title=request.values.get('title')
            example.source=request.values.get('source')
            example.description=request.values.get('description')
            example.public = Example.bool_to_redis_bool(request.values.get('public'))
            example.fingerprint=request.values.get('fingerprint')
            example.sortnum=request.values.get('sortnum')
            example.save()
            log.info(f'example_edit: {id} edited and saved {example}')
            es.build_mappings()
        else:
            log.warning('form did not validate')
        return render_template('example.html', form=form, title='Example Edit')

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
