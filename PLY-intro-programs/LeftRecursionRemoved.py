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
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t

def t_error(t): 
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)


precedence = (
	('left', 'PLUS'),
)

def p_statement_start(p):
	'E : F T'
	
	
def p_statement_second(p):
	'''T : PLUS F T
	| '''
	

def p_statement_num(p):
	"F : NUM"
	

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

