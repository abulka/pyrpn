from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField, StringField
from examples import example_01


class MyForm(FlaskForm):
    source = TextAreaField('source', default=example_01['source'], validators=[]) #, validators=[DataRequired()])
    comments = BooleanField('Generate comments', default=False)
    line_numbers = BooleanField('Generate line numbers', default=False)

class ExampleForm(FlaskForm):
    source = TextAreaField('source', default=example_01['source'], validators=[])
    title = StringField('title', default='Untitled')
    description = TextAreaField('description', default='Enter a description here')
    public = BooleanField('makepublic', default=False)
