'''
Compiling error support
Gives a detailed error messages in the output

Usage:
    error(line_no=line_no_where_the_error_happened, error_message='some error explaining message', source="filename.src | TextBox")
    errors_count()
    clear_errors()
'''

import sys

_errors_num = 0

def error(line_no, error_message, source=None):
    '''
    Display a compilation error
    '''

    if source:
        error_message = 'ERROR @ LINE {src}:{line}: {msg}'.format(src=source, line=line_no, msg=error_message)
    else:
        error_message = 'ERROR @ LINE {line}: {msg}'.format(line=line_no, msg=error_message)
    print(error_message, file=sys.stderr)

    global _errors_num
    _errors_num += 1


def errors_count():
    '''
    Returns the number of errors encountered during the compilation
    '''

    return _errors_num


def clear_errors():
    '''
    Clears encountered errors count
    '''

    global _errors_num
    _errors_num = 0
