from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email
from textwrap import dedent

sample_source = dedent("""
    def demo():
        total = 0
        for i in range(10):
            result = calc_something(i, 5)
            aview('Counter ', i, ' result= ', total)
            total += result
        aview('Final total was: ', total)
        
    def calc_something(a,b):
        # adds two numbers then squares them
        return (a + b)**2
""")

class MyForm(FlaskForm):
    source = TextAreaField('source', default=sample_source, validators=[]) #, validators=[DataRequired()])
    comments = BooleanField('Generate comments', default=False)
    line_numbers = BooleanField('Generate line numbers', default=False)
