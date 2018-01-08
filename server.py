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
    description = attrib(default='this is a title')
    source = attrib(default='code goes here')
    public = attrib(default=True)  # true or false I suppose - is this supported?

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

    return render_template('index.html', form=form, rpn=rpn, rpn_free42=rpn_free42)


def do(source, comments=True, linenos=True):
    program = parse(source)
    rpn = program.lines_to_str(comments=comments, linenos=linenos)
    return rpn


@app.route('/examples')
def list_examples():
    if len(Example.ids()) == 0:
        example = Example(**example_01)  # create the first example
        log.info('first example re-created', example.asdict)
        # return f'<html><body><pre>{example}</pre></body></html>'
    examples_data = [Example.get(id) for id in Example.ids()]
    return render_template('examples_list.html', examples=examples_data, title="Examples")


@app.route('/example', methods=['GET', 'POST'])
def edit_example():
    """
    This should take a form to edit it.  If no param then create a new blank form and save to a new entry in redis.
    :return:
    """
    form = ExampleForm(request.form)
    if request.method == 'POST' and form.validate():
        print('validated OK')
        example = Example(
            title=request.values.get('title'),
            source=request.values.get('source'),
            description=request.values.get('description'),
            public=request.values.get('public'),
        )
        print(example)
    else:
        # You probably don't have args at this route with GET
        # method, but if you do, you can access them like so:
        yourarg = request.args.get('argname')

    return render_template('example.html', form=form)

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if flask.request.method == 'POST':
#         username = flask.request.values.get('user') # Your form's
#         password = flask.request.values.get('pass') # input names
#         your_register_routine(username, password)
#     else:
#         # You probably don't have args at this route with GET
#         # method, but if you do, you can access them like so:
#         yourarg = flask.request.args.get('argname')
#         your_register_template_rendering(yourarg)


@app.route('/help')
def help():
    return render_template('help.html')

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
