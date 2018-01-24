#!/usr/bin/python3
import sys
import ply.lex as lex
import ply.yacc as yacc


tokens = (
        'NUM', 'PLUS',
)

t_PLUS = r'\+'
t_ignore = " \t\n"
def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_error(t): 
	print("Illegal character %s" % t.value[0])
	t.lexer.skip(1)

precedence = (
	('left', 'PLUS'),
)


def p_statement_number(p):
	'E : NUM'
	p[0]=p[1]
	print("Found an expression consisting of a number \n")

def p_statement_add(p):
	'E : E PLUS E'
	p[0]=p[1]+p[3]
	print("Found a plus expression \n")

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
	print("Enter the Expression")
	data = sys.stdin.readline()
	process(data)

