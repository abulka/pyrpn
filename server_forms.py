from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField, StringField
from examples import example_01
from textwrap import dedent

class MyForm(FlaskForm):
    source = TextAreaField('source', default=example_01['source'], validators=[]) #, validators=[DataRequired()])
    comments = BooleanField('Generate comments', default=False)
    line_numbers = BooleanField('Generate line numbers', default=False)

class ExampleForm(FlaskForm):
    source = TextAreaField('source', default='', validators=[])
    title = StringField('title', default='Untitled')
    description = TextAreaField('description', default=dedent("""
        <p>Enter a description here<p>    
        <p>Add some more information here.  Use <b>html tags</b> if you like.<p>
        <h3>HP42S result</h3>    
        <p>The result of this will be some flashing on the screen 
            followed by the answer.</p>
    """))
    public = BooleanField('make public', default=True)
