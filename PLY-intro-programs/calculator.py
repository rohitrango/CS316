#!/usr/bin/python3

import sys
import ply.lex as lex
import ply.yacc as yacc


tokens = (
        'NAME', 'NUMBER',
        'PLUS', 'MINUS', 'EXP', 'TIMES', 'DIVIDE', 'EQUALS',
        'LPAREN', 'RPAREN',
)


t_ignore = " \t\n"

t_PLUS = r'\+'
t_MINUS = r'-'
t_EXP = r'\*\*'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t


def t_error(t): 
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)

# Parsing rules
precedence = (
	('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('left', 'EXP'),
        ('right', 'UMINUS'),
)

def p_statement_assign(p):
	'statement : NAME EQUALS expression'
	p[1]=p[3]

def p_statement_expr(p):
        'statement : expression'
        print(p[1])

def p_expression_binop(p):
        """
        expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EXP expression
        """
        # print [repr(p[i]) for i in range(0,4)]
        if p[2] == '+':
            p[0] = p[1] + p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]
        elif p[2] == '*':
            p[0] = p[1] * p[3]
        elif p[2] == '/':
            p[0] = p[1] / p[3]
        elif p[2] == '**':
            p[0] = p[1] ** p[3]

def p_expression_uminus(p):
        'expression : MINUS expression %prec UMINUS'
        p[0] = -p[2]

def p_expression_group(p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

def p_expression_number(p):
        'expression : NUMBER'
        p[0] = p[1]

def p_expression_name(p):
        'expression : NAME'
        try:
            p[0] = p[1]
        except LookupError:
            print("Undefined name '%s'" % p[1])
            p[0] = 0

def p_error(p):
	if p:
		print("syntax error at {0}".format(p.value))
	else:
		print("syntax error at EOF")		

def process(data):
	lex.lex()
	yacc.yacc()
	yacc.parse(data)

if __name__ == "__main__":
	print("Enter the Equation")
	data = sys.stdin.readline()
	process(data)
