'''
A scanner

Inputs:
    TINY language snippet code (multiple lines of code written in TINY language syntax)

Output:
    List of (tokenvalue, tokentype) in a file

Example:
    x, identifier
    :=, assign
    4, number

Reserved Keywords:
    IF     : 'if'
    THEN   : 'then'
    ELSE   : 'else'
    END    : 'end'
    REPEAT : 'repeat'
    UNTIL  : 'until'
    READ   : 'read'
    WRITE  : 'write'

Special Symbols:
    PLUS   : '+'
    MINUS  : '-'
    TIMES  : '*'
    DIVIDE : '/'
    EQUAL  : '='
    LESS   : '<'
    LPAREN : '('
    RPAREN : ')'
    SEMI   : ';'
    ASSIGN : ':='

Others:
    IDENTIFIER  : One or more letters
    NUMBER      : One or more digit

Comments: no nesting allowed
    { ... }

White Spaces:
    BLANK   : ' '
    TAB     : '\t'
    NEWLINE : '\n'

Errors:
    ERROR @ LINE lineno: Unterminated comment
    ERROR @ LINE lineno: Illegal character after `:`
'''

from errors import error


class States(object):
    START = 0
    INNUM = 1
    INID = 2
    INASSIGN = 3
    INCOMMENT = 4


class TinyScanner(object):

    reserved_keywords = {
        'if'     : 'IF',
        'then'   : 'THEN',
        'else'   : 'ELSE',
        'end'    : 'END',
        'repeat' : 'REPEAT',
        'until'  : 'UNTIL',
        'read'   : 'READ',
        'write'  : 'WRITE'
    }
    special_symbols = {
        '+'  : 'PLUS',
        '-'  : 'MINUS',
        '*'  : 'TIMES',
        '/'  : 'DIVIDE',
        '='  : 'EQUAL',
        '<'  : 'LESS',
        '('  : 'LPAREN',
        ')'  : 'RPAREN',
        ';'  : 'SEMI'
    }

    white_spaces = ' \t\n'
    digits = '0123456789'
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    comment_open = '{'
    comment_close = '}'

    stream = ''

    @staticmethod
    def tokenize(input):
        stream = input + ' '
        line_no = 1

        current_state = States.START
        lookahead = False
        value = ''
        
        i = 0
        while i < len(stream):
            if lookahead:
                i -= 1
                lookahead = False
            c = stream[i]

            if current_state is States.START:
                if c in TinyScanner.white_spaces:
                    if c is '\n':
                        line_no += 1
                elif c in TinyScanner.digits:
                    value += c
                    current_state = States.INNUM
                elif c in TinyScanner.chars:
                    value += c
                    current_state = States.INID
                elif c in TinyScanner.special_symbols:
                    yield c, TinyScanner.special_symbols[c], line_no
                elif c is ':':
                    current_state = States.INASSIGN
                elif c in TinyScanner.comment_open:
                    current_state = States.INCOMMENT
            elif current_state is States.INNUM:
                if c in TinyScanner.digits:
                    value += c
                else:
                    yield int(value), 'NUMBER', line_no
                    value = ''
                    lookahead = True
                    current_state = States.START
            elif current_state is States.INID:
                if c in TinyScanner.chars:
                    value += c
                else:
                    if value in TinyScanner.reserved_keywords:
                        yield value, TinyScanner.reserved_keywords[value], line_no
                    else:
                        yield value, 'IDENTIFIER', line_no
                    value = ''
                    lookahead = True
                    current_state = States.START
            elif current_state is States.INASSIGN:
                if c is '=':
                    yield ':=', 'ASSIGN', line_no
                    current_state = States.START
                else:
                    error(line_no, 'Illegal character after `:`')
                    current_state = States.START
            elif current_state is States.INCOMMENT:
                if c in TinyScanner.comment_close:
                    current_state = States.START
                elif c is '\n':
                    line_no += 1
            
            i += 1
        
        if current_state is States.INCOMMENT:
            error(line_no, 'Unterminated comment')
