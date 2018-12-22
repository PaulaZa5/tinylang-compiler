'''
A parser

Inputs:
    List of (tokenvalue, tokentype) in a file

Output:
    Syntax tree as a graph

Grammer:
    PROGRAM       → STMT_SEQUENCE
    STMT_SEQUENCE → STATEMENT {SEMI STATEMENT}
                  | STATEMENT
    STATEMENT     → IF_STMT
                  | REPEAT_STMT
                  | ASSIGN_STMT
                  | READ_STMT
                  | WRITE_STMT
    IF_STMT       → IF EXP THEN STMT_SEQUENCE [ELSE STMT_SEQUENCE] END
    REPEAT_STMT   → REPEAT STMT_SEQUENCE UNTIL EXP
    ASSIGN_STMT   → IDENTIFIER ASSIGN EXP
    READ_STMT     → READ IDENTIFIER
    WRITE_STMT    → WRITE EXP
    EXP           → SIMPLE_EXP [COMPARISON_OP SIMPLE_EXP]
    COMPARISON_OP → LESS
                  | EQUAL
    SIMPLE_EXP    → TERM {ADD_OP TERM}
    ADD_OP        → PLUS
                  | MINUS
    TERM          → FACTOR {MUL_OP FACTOR}
    MUL_OP        → TIMES
                  | DIVIDE
    FACTOR        → LPAREN EXP RPAREN
                  | NUMBER
                  | IDENTIFIER

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

from tiny_scanner import TinyScanner
from errors import error
import treelib as tl

Tokenize = TinyScanner.tokenize

class ParseTree(tl.Tree):

    def __init__(self, root_id, root_text, **data):
        super(ParseTree, self).__init__()
        '''tag=root_text.replace('\n', '') removed to avoid the library from sorting the nodes alphabetically'''
        constant_data = {'label': root_text, 'shape': 'box', 'style': 'filled', 'fontname': 'Courier', 'fontcolor': 'white', 'fontsize': '10'}
        self.create_node(tag='a' , identifier=root_id, data={**constant_data, **data})

    def add_node_to_parent(self, node_id, node_text, parent_id, **data):
        '''tag=node_text.replace('\n', '') removed to avoid the library from sorting the nodes alphabetically'''
        constant_data = {'label': node_text, 'shape': 'box', 'style': 'filled', 'fontname': 'Courier', 'fontcolor': 'white', 'fontsize': '10'}
        self.create_node(tag='a' , identifier=node_id, parent=parent_id, data={**constant_data, **data})

    def add_subtree_to_tree(self, subtree, node_id):
        self.paste(node_id, subtree)

class TinyParser(object):

    symbols = {
        'if'         : 'IF',
        'then'       : 'THEN',
        'else'       : 'ELSE',
        'end'        : 'END',
        'repeat'     : 'REPEAT',
        'until'      : 'UNTIL',
        'read'       : 'READ',
        'write'      : 'WRITE',
        '+'          : 'PLUS',
        '-'          : 'MINUS',
        '*'          : 'TIMES',
        '/'          : 'DIVIDE',
        '='          : 'EQUAL',
        '<'          : 'LESS',
        '('          : 'LPAREN',
        ')'          : 'RPAREN',
        ';'          : 'SEMI',
        ':='         : 'ASSIGN',
        'id'         : 'IDENTIFIER',
        'num'        : 'NUMBER'
    }

    def __init__(self, input):
        self.tokens = Tokenize(input)
        self.token = ('', '', '')
        self.next_token()
        self.node_id_counter = 0

    def next_node_id(self):
        self.node_id_counter += 1
        return self.node_id_counter

    def next_token(self):
        try:
            self.token = self.tokens.__next__()
        except StopIteration:
            self.token = ('', '', '')

    def check_current(self, check):
            if self.symbols[check] is self.token[1]:
                return True
            return False

    def accept(self, in_token):
        if self.check_current(in_token):
            self.next_token()
            return True
        
        return False

    def expect(self, in_token):
        if self.accept(in_token):
            return True
        error(self.token[2], 'Unexpected symbol.', 'expect ' + str(in_token))
        return False

    def pro_factor(self):
        tree, root_id = '', 0
        temp_token_txt = self.token[0]
        if self.accept('('):
            tree, root_id = self.pro_exp()
            self.expect(')')
        elif self.accept('num'):
            root_id = self.next_node_id()
            tree = ParseTree(root_id, 'const\n(' + str(temp_token_txt) + ')', shape='ellipse')
        elif self.accept('id'):
            root_id = self.next_node_id()
            tree = ParseTree(root_id, 'id\n(' + temp_token_txt + ')', shape='ellipse')
        else:
            error(self.token[2], 'Unexpected symbol.', 'factor')
        return tree, root_id

    def pro_mul_op(self):
        if self.accept('*'):
            return '*'
        elif self.accept('/'):
            return '/'
        else:
            error(self.token[2], 'Unexpected symbol.', 'mul_op')

    def pro_term(self):
        tree, root_id = self.pro_factor()
        while self.check_current('*') or self.check_current('/'):
            temp_tree, temp_id = tree, root_id
            char = self.pro_mul_op()
            root_id = self.next_node_id()
            tree = ParseTree(root_id, 'op\n(' + char + ')', shape='ellipse')
            tree.add_subtree_to_tree(temp_tree, root_id)
            temp_tree, temp_id = self.pro_factor()
            tree.add_subtree_to_tree(temp_tree, root_id)
        return tree, root_id

    def pro_add_op(self):
        if self.accept('+'):
            return '+'
        elif self.accept('-'):
            return '-'
        else:
            error(self.token[2], 'Unexpected symbol.', 'add_op')

    def pro_simple_exp(self):
        tree, root_id = self.pro_term()
        while self.check_current('+') or self.check_current('-'):
            temp_tree, temp_id = tree, root_id
            char = self.pro_add_op()
            root_id = self.next_node_id()
            tree = ParseTree(root_id, 'op\n(' + char + ')', shape='ellipse')
            tree.add_subtree_to_tree(temp_tree, root_id)
            temp_tree, temp_id = self.pro_term()
            tree.add_subtree_to_tree(temp_tree, root_id)
        return tree, root_id

    def pro_comparison_op(self):
        if self.accept('<'):
            return '<'
        elif self.accept('='):
            return '='
        else:
            error(self.token[2], 'Unexpected symbol.', 'comparison_op')

    def pro_exp(self):
        tree, root_id = self.pro_simple_exp()
        if self.check_current('<') or self.check_current('='):
            temp_tree, temp_id = tree, root_id
            char = self.pro_comparison_op()
            root_id = self.next_node_id()
            tree = ParseTree(root_id, 'op\n(' + char + ')', shape='ellipse')
            tree.add_subtree_to_tree(temp_tree, root_id)
            temp_tree, temp_id = self.pro_simple_exp()
            tree.add_subtree_to_tree(temp_tree, root_id)
        return tree, root_id

    def pro_write_stmt(self):
        tree, root_id = '', 0
        if self.accept('write'):
            temp_tree, temp_id = self.pro_exp()
            root_id = self.next_node_id()
            tree = ParseTree(root_id, 'write')
            tree.add_subtree_to_tree(temp_tree, root_id)
        else:
            error(self.token[2], 'Unexpected symbol.', 'write_stmt')
        return tree, root_id

    def pro_read_stmt(self):
        tree, root_id = '', 0
        if self.accept('read'):
            temp_token_txt = self.token[0]
            self.expect('id')
            root_id = self.next_node_id()
            tree = ParseTree(root_id, 'read\n(' + temp_token_txt + ')')
        else:
            error(self.token[2], 'Unexpected symbol.', 'read_stmt')
        return tree, root_id

    def pro_assign_stmt(self):
        tree, root_id = '', 0
        temp_token_txt = self.token[0]
        if self.accept('id'):
            root_id = self.next_node_id()
            tree = ParseTree(root_id, 'assign\n(' + temp_token_txt + ')')
            self.expect(':=')
            temp_tree, temp_id = self.pro_exp()
            tree.add_subtree_to_tree(temp_tree, root_id)
        else:
            error(self.token[2], 'Unexpected symbol.', 'assign_stmt')
        return tree, root_id

    def pro_repeat_stmt(self):
        tree, root_id = '', 0
        if self.accept('repeat'):
            temp_tree, temp_id = self.pro_stmt_sequence()
            root_id = self.next_node_id()
            tree = ParseTree(root_id, 'repeat')
            tree.add_subtree_to_tree(temp_tree, root_id)
            self.expect('until')
            temp_tree, temp_id = self.pro_exp()
            tree.add_subtree_to_tree(temp_tree, root_id)
        else:
            error(self.token[2], 'Unexpected symbol.', 'repeat_stmt')
        return tree, root_id

    def pro_if_stmt(self):
        tree, root_id = '', 0
        if self.accept('if'):
            temp_tree, temp_id = self.pro_exp()
            root_id = self.next_node_id()
            tree = ParseTree(root_id, 'if')
            tree.add_subtree_to_tree(temp_tree, root_id)
            self.expect('then')
            temp_tree, temp_id = self.pro_stmt_sequence()
            tree.add_subtree_to_tree(temp_tree, root_id)
            if self.accept('else'):
                temp_tree, temp_id = self.pro_stmt_sequence()
                tree.add_subtree_to_tree(temp_tree, root_id)
            self.expect('end')
        else:
            error(self.token[2], 'Unexpected symbol.', 'if_stmt')
        return tree, root_id

    def pro_statement(self):
        tree, root_id = '', 0
        if self.check_current('if'):
            tree, root_id = self.pro_if_stmt()
        elif self.check_current('repeat'):
            tree, root_id = self.pro_repeat_stmt()
        elif self.check_current('id'):
            tree, root_id = self.pro_assign_stmt()
        elif self.check_current('read'):
            tree, root_id = self.pro_read_stmt()
        elif self.check_current('write'):
            tree, root_id = self.pro_write_stmt()
        else:
            error(self.token[2], 'Unexpected symbol.', 'statement')
        return tree, root_id

    def pro_stmt_sequence(self):
        created_head = False
        tree, root_id = self.pro_statement()
        while self.accept(';'):
            if not created_head:
                temp_tree, temp_id = tree, root_id
                root_id = self.next_node_id()
                tree = ParseTree(root_id, 'stmt_sequence')
                tree.add_subtree_to_tree(temp_tree, root_id)
                created_head = True
            temp_tree, temp_id = self.pro_statement()
            tree.add_subtree_to_tree(temp_tree, root_id)
        return tree, root_id

    def pro_program(self):
        tree, root_id = self.pro_stmt_sequence()
        return tree, root_id

    @staticmethod
    def parse(input):
        parser = TinyParser(input)
        tree, root_id = parser.pro_program()
        return tree, root_id
