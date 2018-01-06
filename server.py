from flask import Flask, render_template, redirect, url_for, request
from parse import parse
import logging
from logger import config_log
from server_forms import MyForm, sample_source
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

# @app.route('/r/', defaults={'path': ''}, methods = ['PUT', 'GET'])
# @app.route('/r/<path:path>', methods = ['PUT', 'GET'])
@app.route('/examples')
def list_examples():

    # if (request.method == 'PUT'):
    #     event = request.json
    #     event['last_updated'] = int(time.time())
    #     event['ttl'] = ttl
    #     db.delete(path) #remove old keys
    #     db.hmset(path, event)
    #     db.expire(path, ttl)
    #     return json.dumps(event), 201
    #
    # if not db.exists(path):
    #     return "Error: thing doesn't exist"

    example1 = {
        'title': 'initial demo',
        'descriptions': 'this is a description',
        'title': sample_source,
    }
    rez = 'Examples:\n'
    EXAMPLES = 'pyrpn.examples'
    print("db.exists('EXAMPLES')", db.exists('EXAMPLES'))
    if not db.exists(EXAMPLES):
        print('creating initial....')
        db.lpush(EXAMPLES, json.dumps(example1))
    else:
        len = db.llen(EXAMPLES)
        print(f'it exists and has length {len}')

    examples = db.lrange(EXAMPLES, 0, -1)
    print(type(examples))
    for example in examples:
        print(example)
        data = json.loads(example)
        rez += f'{data["title"]}\n'

    # event = db.hgetall('pyrpn.examples')
    # if event:
    #     # for k, v in event.items():
    #     #     rez += f'{k} = {v}'
    #     #     rez += '\n'
    #     for k, v in event.items():
    #         rez += f'{k} = {v}'
    #         rez += '\n'
            # event["ttl"] = db.ttl(path)
    #cast integers accordingly, nested arrays, dicts not supported for now  :(
    # dict_with_ints = dict((k,int(v) if isInt(v) else v) for k,v in event.iteritems())
    # return json.dumps(dict_with_ints), 200
    return f'<html><body><pre>{rez}</pre></body></html>'


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
