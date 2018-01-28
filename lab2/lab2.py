import ply.lex as lex
import ply.yacc as yacc
import sys

tokens = ['ID', 'STAR', 'AND', 'NUM', 'LPAREN', 'RPAREN', 'COMMA', 'LCURL', 'RCURL', 'SEMICOLON', 'EQUALS', 
			'INT', 'VOID', 'MAIN']

t_ID = r'[a-zA-Z][a-zA-Z0-9]*'
t_STAR = r'\*'
t_AND = r'\&'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r'\,'
t_LCURL = r'\{'
t_RCURL = r'\}'
t_SEMICOLON = r'\;'
t_EQUALS = r'\='

ptr_num = 0
eq_num = 0
stat_num = 0

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

def t_COMMENT(t):
	r'\/\/.*'
	pass
# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)

'''
-----------------------------------------------------------------------
Parser
-----------------------------------------------------------------------

'''

# This defines our program
def p_def_prog(p):
	''' prog : VOID MAIN LPAREN RPAREN LCURL body RCURL
			 | VOID MAIN LPAREN RPAREN LCURL RCURL
	'''
	# print("Program defined.")
	p[0] = "".join(map(lambda x: str(x), p[1:]))


def p_def_body(p):
	''' body : stmt body
			 | stmt
	'''
	p[0] = "".join(map(lambda x: str(x), p[1:]))

def p_def_stmt(p):
	''' stmt : decl SEMICOLON 
			 | assgn_list SEMICOLON
	'''
	p[0] = "".join(map(lambda x: str(x), p[1:]))

def p_def_assgn_list(p):
	''' assgn_list : assgn_list COMMA assgn 
			  | assgn 
	'''
	p[0] = "".join(map(lambda x: str(x), p[1:]))

def p_def_assgn(p):
	''' assgn : ptr_assgn
	 		  | num_assgn
	'''
	p[0] = "".join(map(lambda x: str(x), p[1:]))

def p_def_decl(p):
	''' decl : INT decl_list
	'''
	p[0] = "".join(map(lambda x: str(x), p[1:]))

def p_def_decl_list(p):
	''' decl_list : decl_list COMMA ID
				 | decl_list COMMA ptr
				 | decl_list COMMA ptr_assgn
				 | ID
				 | ptr
				 | ptr_assgn
	'''
	global stat_num, ptr_num
	# print([repr(p[i]) for i in range(len(p))])
	p[0] = "".join(map(lambda x: str(x), p[1:]))
	last_token = repr(p[len(p)-1])[1]
	if last_token == "*":
		ptr_num += 1
	else:
		stat_num += 1


def p_def_ptr_assgn(p):
	''' ptr_assgn : ptr EQUALS ptr_expr '''
	global eq_num
	eq_num += 1
	p[0] = "".join(map(lambda x: str(x), p[1:]))


def p_def_num_assgn(p):
	''' num_assgn : ID EQUALS addr '''
	global eq_num
	eq_num += 1
	p[0] = "".join(map(lambda x: str(x), p[1:]))	

def p_def_ptr_expr(p):
	''' ptr_expr : ptr EQUALS ptr_expr
				| NUM
				| ptr
	'''
	global eq_num
	if len(p) > 2:
		eq_num+=1
		p[0] = "".join(map(lambda x: str(x), p[1:]))
	else:
		p[0] = str(p[1])


def p_def_ptr(p):
	'''  ptr : STAR ID
	'''
	p[0] = p[1] + p[2]


def p_def_addr(p):
	''' addr : AND ID
	'''
	p[0] = p[1] + p[2]

def p_error(p):
	if p:
		print("syntax error at {0}, line no. {1}".format(p.value, p.lineno))
	else:
		print("syntax error at EOF.")
	sys.exit(0)


if __name__ == "__main__":

	lexer = lex.lex()
	yacc.yacc()
	filename = sys.argv[1]
	with open(filename, 'r') as f:
		data = f.read()
	# print(data)
	lex.input(data)
	# while True:
	# 	tok = lexer.token()
	# 	if not tok:
	# 		break
	# 	print(repr(tok))
	yacc.parse(data)
	print(stat_num)
	print(ptr_num)
	print(eq_num)