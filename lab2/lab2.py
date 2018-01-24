import ply.lex as lex
import ply.yacc as yacc
import sys

tokens = ['ID', 'PTR', 'ADDR', 'NUM', 'LPAREN', 'RPAREN', 'COMMA', 'LCURL', 'RCURL', 'SEMICOLON', 'EQUALS', 
			'INT', 'VOID', 'MAIN']

t_ID = r'[a-zA-Z][a-zA-Z0-9]*'
t_PTR = r'\*[a-zA-Z][a-zA-Z0-9]*'
t_ADDR = r'\&[a-zA-Z][a-zA-Z0-9]*'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r'\,'
t_LCURL = r'\{'
t_RCURL = r'\}'
t_SEMICOLON = r'\;'
t_EQUALS = r'\='

def t_NUM(t):
	r'(\+|\-)?[0-9]+'
	t.value = int(t.value)
	return t

def t_INT(t):
	r'int'
	return t

def t_VOID(t):
	r'void'
	return t

# careful!
def t_MAIN(t):
	r'main'
	return t

def t_newline(t):
	r'\n+'
	t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)


if __name__ == "__main__":

	lexer = lex.lex()
	# yacc.yacc()
	filename = sys.argv[1]
	with open(filename, 'r') as f:
		data = f.read()
	print(data)
	lex.input(data)
	while True:
		tok = lexer.token()
		if not tok:
			break
		print(repr(tok))

