from flask import Flask, render_template, redirect, url_for, request
from parse import parse
import logging
from logger import config_log
from server_forms import MyForm, ExampleForm
from examples import example_01
import redis
import json
from attr import attrs, attrib
from lib import cheap_redis_db

log = logging.getLogger(__name__)
config_log(log)

# db = redis.StrictRedis()
db = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)
cheap_redis_db.config.set_connection(db)

app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))


@attrs
class Example(cheap_redis_db.CheapRecord):
    title = attrib(default='Untitled')
    description = attrib(default='Description here')
    source = attrib(default='python source code goes here')
    public = attrib(default='')  # true or false is not supported in redis - only strings are.  Even integers are just strings

cheap_redis_db.config.register_class(Example, namespace='pyrpn')


@app.route('/', methods=["GET", "POST"])
def index():
    rpn = ''
    rpn_free42 = ''
    form = MyForm()
    if form.validate_on_submit():
        program = parse(form.source.data)
        rpn = program.lines_to_str(comments=form.comments.data, linenos=form.line_numbers.data)
        rpn_free42 = program.lines_to_str(comments=False, linenos=True)
    else:
        rpn = rpn_free42 = 'Press Convert'

    return render_template('index.html', form=form, rpn=rpn, rpn_free42=rpn_free42, title='source code converter')


def do(source, comments=True, linenos=True):
    program = parse(source)
    rpn = program.lines_to_str(comments=comments, linenos=linenos)
    return rpn


@app.route('/examples')
def examples_list():
    if len(Example.ids()) == 0:
        example = Example(**example_01)  # create the first example
        log.info('first example re-created', example.asdict)
        # return f'<html><body><pre>{example}</pre></body></html>'
    examples_data = [Example.get(id) for id in Example.ids()]
    return render_template('examples_list.html', examples=examples_data, title="Examples")


def redis_bool_to_bool(redis_val):
    # hack to convert redis bool of 'y'/'' into real bool
    return redis_val == 'yes'

def bool_to_redis_bool(val):
    # hack to convert bool into redis bool of 'y'/''.  Returns the value to store into redis
    return 'yes' if val else ''


@app.route('/example', methods=['GET', 'POST'])
def example_create():
    """
    Handle GET blank initial forms and POST creating new entries.
    """
    if request.method == 'POST':
        log.debug(f'example_create POST public {request.values.get("public")}')
        form = ExampleForm(request.form)
        # example = Example(**dict(request.values))  # why doesn't this work?
        if form.validate():
            example = Example(
                title=request.values.get('title'),
                source=request.values.get('source'),
                description=request.values.get('description'),
                public = bool_to_redis_bool(request.values.get('public')),
            )
            log.info(example)
            return redirect(url_for('example_edit', id=example.id))
    else:  # GET
        form = ExampleForm()
    return render_template('example.html', form=form, title='Example Edit')

@app.route('/example/<int:id>', methods=['GET', 'POST'])
def example_edit(id):
    """
    Handle GET existing example and POST updating it.  Forms cannot send put verb.
    If pass param ?delete=1 then do a DELETE.  Forms cannot send delete verb.
    """
    delete = request.args.get('delete')  # Wish forms could send delete verb properly...
    example = Example.get(id)
    log.info(f'example_edit: id {id} delete flag {delete} example is {example}')

    if request.method == 'GET' and delete:
        example.delete()
        return redirect(url_for('examples_list'))  # 'url_for' takes the name of view def

    if request.method == 'GET':
        dic = example.asdict
        dic['public'] = redis_bool_to_bool(example.public)
        form = ExampleForm(**dic)
        return render_template('example.html', form=form, title='Example Edit')

    elif request.method == 'POST':  # Wish forms could send put verb properly...
        form = ExampleForm(request.form)
        if form.validate():
            example.title=request.values.get('title')
            example.source=request.values.get('source')
            example.description=request.values.get('description')
            # example.public=request.values.get('public')
            example.public = bool_to_redis_bool(request.values.get('public'))
            example.save()
            log.info(f'example_edit: {id} edited and saved {example}')
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
