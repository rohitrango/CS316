'''
Assignment A2
Team members: 
1. Rohit Kumar Jena (150050061)
2. Walter Berggren  (17V051001)
'''
import ply.lex as lex
import ply.yacc as yacc
import sys

tokens = ['ID', 'STAR', 'AND', 'NUM', 'LPAREN', 'RPAREN', 'COMMA', 'LCURL', 'RCURL', 'SEMICOLON', 'EQUALS', 
			'INT', 'VOID', 'MAIN',
			# Symbols 
			'PLUS', 'MINUS', 'SLASH',
		 ]

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

# New tokens for A3
t_PLUS = r'\+'
t_MINUS = r'\-'
t_SLASH = r'\/'

# Variables for A1
ptr_num = 0
eq_num = 0
stat_num = 0

# Variables for A2
ast_list = []


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
Data Structure for Abstract Syntax Tree
-----------------------------------------------------------------------
'''

# Generate Tree in format
# def generateTreeFormat(node, depth=0):
	# pass
	# delim = "\t"*depth
	# if node.operator in ['VAR', 'CONST']:
	# 	result = delim + node.operator + "(" + node.name + ")\n"
	# else:
	# 	result = delim + node.operator + "\n" + \
	# 			 delim + "(\n"
	# 	for n in node.operands[:-1]:
	# 		result += generateTreeFormat(n, depth+1)
	# 		result += (delim + "\t,")
	# 	result += generateTreeFormat(node.operands[-1], depth+1)
	# 	result += delim + "\t" + ")\n"
	# return result


class AbstractSyntaxTreeNode():

	def __init__(self, operator, name=None, operands=[]):
		self.operator = operator
		self.name = name
		self.operands = operands

	def addChild(self, child):
		self.operands.append(child)

	def __repr__(self, depth=0):
		if len(self.operands) == 0:
			return depth*"\t" + self.operator + "(" + self.name + ")"
		else:
			return depth*"\t" + self.operator + "\n" + depth*"\t" + "(\n" \
					+ ("\n" + (depth+1)*"\t" + ",\n").join(map(lambda x: x.__repr__(depth+1), self.operands)) + "\n" + depth*"\t" + ")" 
		# return generateTreeFormat(self)

	def isConst(self):
		if len(self.operands) == 0:
			return self.operator == "CONST"
		else:
			return all(x.isConst() for x in self.operands)

'''
-----------------------------------------------------------------------
Parser
-----------------------------------------------------------------------
'''

precedence = (
	('left', 'PLUS', 'MINUS'),
	('left', 'STAR', 'SLASH'),
	('right', 'UMINUS'),

)


# This defines our program
def p_def_prog(p):
	''' prog : VOID MAIN LPAREN RPAREN LCURL body RCURL
			 | VOID MAIN LPAREN RPAREN LCURL RCURL
	'''
	# print("Program defined.")
	# p[0] = "".join(map(lambda x: str(x), p[1:]))
	p[0] = dict([(i, v) for i, v in enumerate(p[1:])])
	# TODO: Remove this later
	# print(json.dumps(p[0], indent=4, sort_keys=True))


def p_def_body(p):
	''' body : stmt body
			 | stmt
	'''
	# p[0] = "".join(map(lambda x: str(x), p[1:]))
	p[0] = dict([(i, v) for i, v in enumerate(p[1:])])


def p_def_stmt(p):
	''' stmt : decl SEMICOLON 
			 | assgn_list SEMICOLON
	'''
	# p[0] = "".join(map(lambda x: str(x), p[1:]))
	p[0] = dict([(i, v) for i, v in enumerate(p[1:])])


def p_def_assgn_list(p):
	''' assgn_list : assgn_list COMMA assgn 
			  | assgn 
	'''
	# p[0] = "".join(map(lambda x: str(x), p[1:]))
	p[0] = dict([(i, v) for i, v in enumerate(p[1:])])


def p_def_assgn(p):
	''' assgn : ptr_assgn
	 		  | num_assgn
	'''
	# p[0] = "".join(map(lambda x: str(x), p[1:]))
	p[0] = dict([(i, v) for i, v in enumerate(p[1:])])


def p_def_decl(p):
	''' decl : INT decl_list
	'''
	# p[0] = "".join(map(lambda x: str(x), p[1:]))
	p[0] = dict([(i, v) for i, v in enumerate(p[1:])])


def p_def_decl_list(p):
	''' decl_list : decl_list COMMA ID
				 | decl_list COMMA ptr
				 | ID
				 | ptr
	'''
	global stat_num, ptr_num
	# print([repr(p[i]) for i in range(len(p))])
	# p[0] = "".join(map(lambda x: str(x), p[1:]))
	p[0] = dict([(i, v) for i, v in enumerate(p[1:])])

	last_token = repr(p[len(p)-1])[1]
	if last_token == "*":
		ptr_num += 1
	else:
		stat_num += 1


def p_def_ptr_assgn(p):
	''' ptr_assgn : ptr EQUALS ptr_expr '''

	p[0] = AbstractSyntaxTreeNode("ASGN", None, [p[1], p[3]])
	ast_list.append(p[0])
	# global eq_num
	# eq_num += 1
	# p[0] = "".join(map(lambda x: str(x), p[1:]))
	# p[0] = dict([(i, v) for i, v in enumerate(p[1:])])

def p_def_num_assgn(p):
	''' num_assgn : ID EQUALS ptr_expr
	'''
	# Allow any expression after a num assignment, except assignments directly to constants
	if p[3].isConst():
		print("Syntax error: Static assignments to constants not allowed")
		raise SyntaxError
	p[1] = AbstractSyntaxTreeNode("VAR", p[1])
	if isinstance(p[3], str):
		p[3] = AbstractSyntaxTreeNode("VAR", p[3])
	p[0] = AbstractSyntaxTreeNode("ASGN", None, [p[1], p[3]])
	ast_list.append(p[0])
	# global eq_num
	# eq_num += 1
	# p[0] = "".join(map(lambda x: str(x), p[1:]))
	# p[0] = dict([(i, v) for i, v in enumerate(p[1:])])



def p_def_ptr_expr(p):
	'''	ptr_expr : ptr_expr PLUS ptr_factor 
				 | ptr_expr MINUS ptr_factor
				 | ptr_factor
	'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		if p[2] == "+":
			s = "PLUS"
		else:
			s = "MINUS"
		p[0] = AbstractSyntaxTreeNode(s, None, [p[1], p[3]])

	# p[0] = dict([(i, v) for i, v in enumerate(p[1:])])
	# p[0] = "".join(map(lambda x: str(x), p[1:]))


def p_def_ptr_factor(p):
	"""
		ptr_factor :  ptr_factor STAR ptr_term
				 	| ptr_factor SLASH ptr_term
				 	| ptr_term
	"""
	if len(p) == 2:
		p[0] = p[1]
	else:
		if p[2] == "*":
			s = "MUL"
		else:
			s = "DIV"
		p[0] = AbstractSyntaxTreeNode(s, None, [p[1], p[3]])

	# p[0] = dict([(i, v) for i, v in enumerate(p[1:])])
	# p[0] = "".join(map(lambda x: str(x), p[1:]))


def p_def_ptr_term(p):
	""" ptr_term :  MINUS ptr_term  		%prec UMINUS
				  | ptr_expr_base
	"""
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = AbstractSyntaxTreeNode("UMINUS", None, [p[2]])

	# p[0] = dict([(i, v) for i, v in enumerate(p[1:])])
	# p[0] = "".join(map(lambda x: str(x), p[1:]))


def p_def_ptr_expr_base(p):
	''' ptr_expr_base : ID
				| NUM
				| ptr
				| addr
				| LPAREN ptr_expr RPAREN
	'''
	if isinstance(p[1], str):
		p[1] = AbstractSyntaxTreeNode("VAR", p[1])
	elif isinstance(p[1], int):
		p[1] = AbstractSyntaxTreeNode("CONST", str(p[1]))

	p[0] = p[1]
	# p[0] = dict([(i, v) for i, v in enumerate(p[1:])])
	# p[0] = "".join(map(lambda x: str(x), p[1:]))
	# global eq_num
	# if len(p) > 2:
	# 	eq_num+=1
	# 	p[0] = "".join(map(lambda x: str(x), p[1:]))
	# else:
	# 	p[0] = str(p[1])


def p_def_ptr(p):
	'''  ptr : STAR ptr 
			 | STAR ID
			 | STAR addr
	'''
	# p[0] = p[1] + p[2]
	if isinstance(p[2], str):
		p[2] = AbstractSyntaxTreeNode("VAR", p[2])

	p[0] = AbstractSyntaxTreeNode("DEREF", None, [p[2]])


def p_def_addr(p):
	''' addr : AND ID
			 | AND ptr
			 | AND addr
	'''
	if isinstance(p[2], str):
		p[2] = AbstractSyntaxTreeNode("VAR", p[2])

	p[0] = AbstractSyntaxTreeNode("ADDR", None, [p[2]])



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
	for l in ast_list:
		print(l)
	# print(stat_num)
	# print(ptr_num)
	# print(eq_num)