'''
Assignment A3
Team members: 
1. Rohit Kumar Jena (150050061)
2. Walter Berggren  (17V051001)
'''
import ply.lex as lex
import ply.yacc as yacc
import sys

tokens = ['ID', 'STAR', 'AND', 'NUM', 'LPAREN', 'RPAREN', 'COMMA', 'LCURL', 'RCURL', 'SEMICOLON', 'EQUALS', 
			# Symbols 
			'PLUS', 'MINUS', 'SLASH',
			# For A3
			'LT', 'GT', 'NOT', 'OR',
		 ]

reserved = {
	'if' 	: 'IF',
	'else'	: 'ELSE',
	'while' : 'WHILE',
	'main'  : 'MAIN',
	'void' 	: 'VOID',
	'int'	: 'INT',
}

tokens += list(reserved.values())

def t_NUM(t):
	r'[0-9]+'
	t.value = int(t.value)
	return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

t_STAR = r'\*'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r'\,'
t_LCURL = r'\{'
t_RCURL = r'\}'
t_SEMICOLON = r'\;'


# Boolean operators
t_EQUALS = r'\='
t_AND = r'\&'
t_LT = r'\<'
t_GT = r'\>'
t_NOT = r'\!'
t_OR = r'\|'


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
cfg_ast = []

def t_newline(t):
	r'\n|\r\n'
	t.lexer.lineno += len(t.value)

def t_COMMENT(t):
	r'\/\/.*'
	pass
# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
	print(t)
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)


'''
-----------------------------------------------------------------------
Data Structure for Abstract Syntax Tree
-----------------------------------------------------------------------
'''

class AbstractSyntaxTreeNode():

	def __init__(self, operator, operands=[], name=None):
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

	('left', 'THEN'),
	('left', 'ELSE'),

	('left', 'PLUS', 'MINUS'),
	('left', 'STAR', 'SLASH'),
	('right', 'UMINUS'),
)


# This defines our program
def p_def_prog(p):
	''' prog : VOID MAIN LPAREN RPAREN LCURL body RCURL
			 | VOID MAIN LPAREN RPAREN LCURL RCURL
	'''
	if len(p) == 7:
		p[0] = AbstractSyntaxTreeNode("PROG", [])
	else:
		p[0] = AbstractSyntaxTreeNode("PROG", [p[6]])


def p_def_body(p):
	''' body : body stmt
			 | stmt
	'''
	if len(p) == 2:
		p[0] = AbstractSyntaxTreeNode("BODY", [p[1]])
	else:
		p[0] = p[1]
		p[0].addChild(p[2])


def p_def_stmt(p):
	''' stmt : decl SEMICOLON 
			 | assgn SEMICOLON
			 | if_stmt 
			 | while_stmt
	'''
	p[0] = p[1]


# Adding for A3 -> if and while
#############################################################

def p_def_if_stmt(p):
	'''
		if_stmt : IF LPAREN ptr_expr RPAREN compound_stmt 				%prec THEN
				| IF LPAREN ptr_expr RPAREN compound_stmt ELSE compound_stmt
	'''
	# Only an if-stmt
	if len(p) == 6:
		p[0] = AbstractSyntaxTreeNode("IF", [p[3], p[5]])
	else:
		p[0] = AbstractSyntaxTreeNode("IF", [p[3], p[5], p[7]])
	cfg_ast.append(p[0])


def p_def_while_stmt(p):
	'''
		while_stmt : WHILE LPAREN ptr_expr RPAREN compound_stmt
	'''
	p[0] = AbstractSyntaxTreeNode("WHILE", [p[3], p[5]])
	cfg_ast.append(p[0])

def p_def_compound_stmt(p):
	'''
		compound_stmt : stmt
					  | LCURL body RCURL
	'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = p[2]


#############################################################

def p_def_assgn(p):
	''' assgn : ptr_assgn
	 		  | num_assgn
	'''
	p[0] = p[1]


def p_def_decl(p):
	''' decl : INT decl_list
	'''
	p[0] = AbstractSyntaxTreeNode("DECL", [p[1]])



def p_def_decl_list(p):
	''' decl_list : decl_list COMMA ID
				 | decl_list COMMA ptr
				 | ID
				 | ptr
	'''
	if len(p) == 2:
		p[0] = AbstractSyntaxTreeNode("DECL_LIST", [p[1]])
	else:
		p[0] = p[1]
		p[0].addChild(p[3])


def p_def_ptr_assgn(p):
	''' ptr_assgn : ptr EQUALS ptr_expr '''

	p[0] = AbstractSyntaxTreeNode("ASGN", [p[1], p[3]])
	ast_list.append(p[0])

def p_def_num_assgn(p):
	''' num_assgn : ID EQUALS ptr_expr
	'''
	# Allow any expression after a num assignment, except assignments directly to constants
	if p[3].isConst():
		print("Syntax error: Static assignments to constants not allowed, line no. {0}".format(p.lineno(1)))
		raise Exception
	p[1] = AbstractSyntaxTreeNode("VAR", [], p[1])
	# if isinstance(p[3], str):
	# 	p[3] = AbstractSyntaxTreeNode("VAR", p[3])
	p[0] = AbstractSyntaxTreeNode("ASGN", [p[1], p[3]])
	ast_list.append(p[0])


def p_def_ptr_expr(p):
	'''	ptr_expr : ptr_expr OR ptr_and_expr 
				 | ptr_and_expr
	'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = AbstractSyntaxTreeNode("OR", [p[1], p[3]])


def p_def_ptr_and_expr(p):
	'''	ptr_and_expr : ptr_and_expr AND ptr_eq_expr 
				 | ptr_eq_expr
	'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = AbstractSyntaxTreeNode("AND", [p[1], p[3]])

def p_def_ptr_eq_expr(p):
	'''	ptr_eq_expr : ptr_eq_expr EQUALS EQUALS ptr_lt_expr
				 | ptr_eq_expr NOT EQUALS ptr_lt_expr
				 | ptr_lt_expr
	'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		if p[2] == "!":
			p[0] = AbstractSyntaxTreeNode("NEQ", [p[1], p[4]])
		else:
			p[0] = AbstractSyntaxTreeNode("EQ", [p[1], p[4]])


def p_def_ptr_lt_expr(p):
	'''	ptr_lt_expr : ptr_lt_expr LT ptr_add_expr
				 | ptr_lt_expr GT ptr_add_expr
				 | ptr_lt_expr LT EQUALS ptr_add_expr
				 | ptr_lt_expr GT EQUALS ptr_add_expr
				 | ptr_add_expr
	'''
	if len(p) == 2:
		p[0] = p[1]
	
	# LT or GT
	elif len(p) == 4:
		s = "LT" if p[2] == "<" else "GT"
		p[0] = AbstractSyntaxTreeNode(s, [p[1], p[3]])

	# LTE or GTE
	else:
		s = "LTE" if p[2] == "<" else "GTE"
		p[0] = AbstractSyntaxTreeNode(s, [p[1], p[4]])


def p_def_ptr_add_expr(p):
	'''	ptr_add_expr : ptr_add_expr PLUS ptr_factor 
				 | ptr_add_expr MINUS ptr_factor
				 | ptr_factor
	'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		if p[2] == "+":
			s = "PLUS"
		else:
			s = "MINUS"
		p[0] = AbstractSyntaxTreeNode(s, [p[1], p[3]])


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
		p[0] = AbstractSyntaxTreeNode(s, [p[1], p[3]])


def p_def_ptr_term(p):
	""" ptr_term :  MINUS ptr_term  		%prec UMINUS
				  | ptr_expr_base
	"""
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = AbstractSyntaxTreeNode("UMINUS", [p[2]])


def p_def_ptr_expr_base(p):
	''' ptr_expr_base : ID
				| NUM
				| ptr
				| addr
				| LPAREN ptr_expr RPAREN
	'''
	if len(p) == 2:
		if isinstance(p[1], str):
			p[1] = AbstractSyntaxTreeNode("VAR", [], p[1])
		elif isinstance(p[1], int):
			p[1] = AbstractSyntaxTreeNode("CONST", [], str(p[1]))

		p[0] = p[1]

	# Support parenthesis
	else:
		p[0] = p[2]


def p_def_ptr(p):
	'''  ptr : STAR ptr 
			 | STAR ID
			 | STAR addr
	'''
	if isinstance(p[2], str):
		p[2] = AbstractSyntaxTreeNode("VAR", [], p[2])

	p[0] = AbstractSyntaxTreeNode("DEREF", [p[2]])


def p_def_addr(p):
	''' addr : AND ID
			 | AND ptr
			 | AND addr
	'''
	if isinstance(p[2], str):
		p[2] = AbstractSyntaxTreeNode("VAR", [],  p[2])

	p[0] = AbstractSyntaxTreeNode("ADDR", [p[2]])



def p_error(p):
	if p:
		print("syntax error at {0}, line no. {1}".format(p.value, p.lineno))
	else:
		print("syntax error at EOF.")
	raise Exception


if __name__ == "__main__":


	lexer = lex.lex()
	yacc.yacc()
	filename = sys.argv[1]

	# read input
	with open(filename, 'r') as f:
		data = f.read()

	lex.input(data)

	# Catch the syntax error
	try:
		yacc.parse(data)
		print("Successfully Parsed")
	except Exception:
		pass

	for l in cfg_ast:
		print(l)
		print("\n")
	# output_file = 'Parser_ast_' + filename + '.txt'	
	# with open(output_file, 'w+') as file:
	# 	for l in ast_list:
	# 		file.write(repr(l) + "\n")
	# 		file.write("\n")
