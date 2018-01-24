import ply.lex as lex
import ply.yacc as yacc
import sys


if __name__ == "__main__":

	lex.lex()
	yacc.yacc()
	filename = sys.argv[1]
	with open(filename, 'r') as f:
		data = f.read()
	print(data)
