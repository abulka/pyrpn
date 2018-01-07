from flask import Flask, render_template, redirect, url_for, request
from parse import parse
import logging
from logger import config_log
from server_forms import MyForm, ExampleForm, sample_source
import redis
import json


log = logging.getLogger(__name__)
config_log(log)

app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

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



db = redis.Redis('localhost') #connect to server

EXAMPLES = 'pyrpn.examples'

@app.route('/examples')
def list_examples():
    """
    In the CLI use
        DEL pyrpn.examples
    to delete examples
    """

    example1 = {
        'title': 'initial demo',
        'description': 'this is a description',
        'code': sample_source,
    }
    rez = 'Examples:\n'
    print("db.exists('EXAMPLES')", db.exists('EXAMPLES'))
    if not db.exists(EXAMPLES):
        print('creating initial....')
        db.lpush(EXAMPLES, json.dumps(example1))
    else:
        len = db.llen(EXAMPLES)
        print(f'examples list exists and has length {len}')

    examples_data = []  # python object
    examples = db.lrange(EXAMPLES, 0, -1)  # redis object (wrapped in python)
    for example in examples:
        data = json.loads(example)  # convert record back into python object
        examples_data.append(data)
        rez += f'{data["title"]}\n'
    print(examples_data)
    # return f'<html><body><pre>{rez}</pre></body></html>'
    return render_template('examples_list.html', examples=examples_data)


@app.route('/example', methods=['GET', 'POST'])
def edit_example():
    """
    This should take a form to edit it.  If no param then create a new blank form and save to a new entry in redis.
    :return:
    """
    form = ExampleForm(request.form)
    if request.method == 'POST' and form.validate():
        print('validated OK')
        example = {
            'title': request.values.get('title'),
            'description': request.values.get('description'),
            'code': request.values.get('source'),
            'public': request.values.get('public'),
        }
        print(example)
        # flash('Thanks for saving')
        db.lpush(EXAMPLES, json.dumps(example))
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
