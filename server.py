from flask import Flask, render_template
from parse import parse
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)

app = Flask(__name__)


# @app.route('/')
# def hello_world():
#     return 'Hello World!'

@app.route('/')
def index():
    with open('research/sample_if_else.py') as fp:
        source = fp.read()
    program = parse(source)
    rpn = program.lines_to_str(comments=True, linenos=True)
    return render_template('index.html', name='andy', rpn=rpn)

@app.route('/hello')
def hello():
    return render_template('hello.html', name='andy')

@app.route('/test')
def test():
    with open('research/sample_if_else.py') as fp:
        source = fp.read()
    program = parse(source)
    rpn = program.lines_to_str(comments=True, linenos=True)
    return f'<html><body><pre>{rpn}</pre></body></html>'



# if __name__ == '__main__':
#     app.run()

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    # app.run(debug=True, host='0.0.0.0')
    app.run(debug=True)
