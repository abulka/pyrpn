# pip install PyQt5
# pip install astviewer
# See https://github.com/titusjan/astviewer

from astviewer.main import view

#view(file_name='research/sample_if_else.py')

view(source_code = 'a + 3', mode='eval')
