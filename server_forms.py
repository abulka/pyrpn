from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField, StringField, IntegerField, validators
from example1 import example_01
from textwrap import dedent

class MyForm(FlaskForm):
    source = TextAreaField('source', default=example_01['source'], validators=[]) #, validators=[DataRequired()])
    comments = BooleanField('Generate comments', default=False)
    line_numbers = BooleanField('Generate line numbers', default=False)

class ExampleForm(FlaskForm):
    source = TextAreaField('Python Source code', default=dedent("""
        def myprogram(param1, param2):
            x = 10 + 1
            return x  # comment
            
        def helper_func():
            pass
    """).strip(), validators=[])
    title = StringField('Title', default='Untitled', validators=[validators.DataRequired()])
    description = TextAreaField('Description', default=dedent("""
        <p>Enter description and commentary here<p>    
        <p>A full <b>html editor</b> is provided incl. the ability to 
            include formatted code snippets.</p>
    """))
    public = BooleanField('Make public', default=True)
    fingerprint = StringField('Fingerprint id', default='')
    sortnum = IntegerField('Sort number', default=0, validators=[validators.NumberRange(message='Range should be between 0 and 999.', min=0, max=999)])
