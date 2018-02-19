from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField, StringField, IntegerField, validators
from textwrap import dedent

class ConverterForm(FlaskForm):
    source = TextAreaField('Source code', validators=[], default=dedent("""
        LBL("untitled")
        
    """).lstrip())
    comments = BooleanField('Generate comments', default=False)
    line_numbers = BooleanField('Generate line numbers', default=False)
    emit_pyrpn_lib = BooleanField('Auto include needed Python RPN Utility Functions', default=True)

class ExampleForm(FlaskForm):
    source = TextAreaField('Python Source code', default=dedent("""
        LBL("untitled")
            
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
    filename = StringField('Filename', default='')
    sortnum = IntegerField('Sort number', default=0, validators=[validators.NumberRange(message='Range should be between 0 and 999.', min=0, max=999)])
    tags = StringField('Tags', default='')
