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

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)

# This defines our program
def p_def_prog(p):
	''' prog : VOID MAIN LPAREN RPAREN LCURL body RCURL
	'''
	# print("Program defined.")
	p[0] = "".join(map(lambda x: str(x), p[1:]))


def p_def_body(p):
	''' body : stmt body
			 | stmt
	'''
	p[0] = "".join(map(lambda x: str(x), p[1:]))

def p_def_stmt(p):
	''' stmt : expr1 SEMICOLON 
			 | expr2 SEMICOLON
	'''
	p[0] = "".join(map(lambda x: str(x), p[1:]))

def p_def_expr2(p):
	''' expr2 : expr2 COMMA equality 
			  | equality 
	'''
	p[0] = "".join(map(lambda x: str(x), p[1:]))

def p_def_equality(p):
	''' equality : equality1
	 			 | equality2
	'''
	p[0] = "".join(map(lambda x: str(x), p[1:]))

def p_def_expr1(p):
	''' expr1 : INT subexpr1
	'''
	p[0] = "".join(map(lambda x: str(x), p[1:]))

def p_def_subexpr1(p):
	''' subexpr1 : subexpr1 COMMA ID
				 | subexpr1 COMMA ptr
				 | subexpr1 COMMA equality1
				 | ID
				 | ptr
				 | equality1
	'''
	global stat_num, ptr_num
	# print([repr(p[i]) for i in range(len(p))])
	p[0] = "".join(map(lambda x: str(x), p[1:]))
	last_token = repr(p[len(p)-1])[1]
	if last_token == "*":
		ptr_num += 1
	else:
		stat_num += 1


def p_def_equality1(p):
	''' equality1 : ptr EQUALS ptrexpr '''
	global eq_num
	eq_num += 1
	p[0] = "".join(map(lambda x: str(x), p[1:]))


def p_def_equality2(p):
	''' equality2 : ID EQUALS addr '''
	global eq_num
	eq_num += 1
	p[0] = "".join(map(lambda x: str(x), p[1:]))	

def p_def_ptrexpr(p):
	''' ptrexpr : ptr EQUALS ptrexpr
				| NUM
				| ptr
				| addr
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