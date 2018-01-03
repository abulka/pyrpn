from flask import Flask, render_template, redirect, url_for
from parse import parse
import logging
from logger import config_log
from server_forms import MyForm

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
    form = MyForm()
    if form.validate_on_submit():
        rpn = do(form.source.data, comments=form.comments.data, linenos=form.line_numbers.data)
    else:
        rpn = 'Press Convert'

    return render_template('index.html', form=form, rpn=rpn)


def do(source, comments=True, linenos=True):
    program = parse(source)
    rpn = program.lines_to_str(comments=comments, linenos=linenos)
    return rpn


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
