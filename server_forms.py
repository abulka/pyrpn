from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email
from textwrap import dedent

sample_source = dedent("""
    def main():
        pass
        
    def useful():  # rpn: export
        pass
        
    main()
    useful()
""")

class MyForm(FlaskForm):
    source = TextAreaField('source', default=sample_source, validators=[]) #, validators=[DataRequired()])
    comments = BooleanField('Generate comments', default=False)
    line_numbers = BooleanField('Generate line numbers', default=False)
