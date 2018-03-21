'''
Assignment A4
Team members: 
1. Rohit Kumar Jena (150050061)
2. Walter Berggren  (17V051001)
'''
import ply.lex as lex
import ply.yacc as yacc
import sys, os
from utils import *
from semantics import *
import json

tokens = ['ID', 'STAR', 'AND', 'NUM', 'NUMFLOAT', 'LPAREN', 'RPAREN', 'COMMA', 'LCURL', 'RCURL', 'SEMICOLON', 'EQUALS', 
			# Symbols 
			'PLUS', 'MINUS', 'SLASH',
			# For A3
			'LT', 'GT', 'NOT', 'OR',
		 ]

reserved = {
	'if' 	: 'IF',
	'else'	: 'ELSE',
	'while' : 'WHILE',

	'void' 	: 'VOID',
	'int'	: 'INT',
	'float'	: 'FLOAT',
}

tokens += list(reserved.values())

def t_NUMFLOAT(t):
	r'\d+\.\d+'
	t.value = float(t.value)
	return t

def t_NUM(t):
	r'\d+'
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
	t.lexer.lineno += 1

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
	''' prog : declarations procedures
	'''
	p[0] = AbstractSyntaxTreeNode("PROG", [p[1], p[2]])
	cfg_ast.append(p[0])

	global_table, messages = generateSymbolTable(p[1])
	global_table['__name__'] = '__global__'
	global_table['__parent__'] = None
	local_tables, global_table, local_messages = generateLocalTables(p[2], global_table)

	messages.extend(local_messages)
	if messages != []:
		for message in messages:
			print(message)
	else:
		print(json.dumps(global_table, indent=4, sort_keys=True))
		for table in local_tables:
			print(json.dumps(table, indent=4, sort_keys=True))

# This takes care of any number of declarations first
def p_def_declaration(p):
	''' 
		declarations : declarations decl SEMICOLON
				     | 
	'''
	if len(p) == 1:
		p[0] = AbstractSyntaxTreeNode("DECLARATIONS", [])
	else:
		p[0] = p[1]
		p[0].addChild(p[2])

# Contain one or more procedures
def p_def_procedures(p):
	'''
		procedures : procedures procedure
				  | procedure 	
	'''
	if len(p) == 2:
		p[0] = AbstractSyntaxTreeNode("PROCEDURES", [p[1]])
	else:
		p[0] = p[1]
		p[0].addChild(p[2])

def p_def_type(p):
	'''
		type : VOID 
			 | INT
			 | FLOAT
	'''
	p[1] = AbstractSyntaxTreeNode("TYPE", [], p[1])
	p[0] = p[1]
	p[0].lineno = p.lineno(1)


# Single procedure
def p_def_procedure(p):
	'''
		procedure : type ID LPAREN params RPAREN LCURL declarations body RCURL
	'''
	# Give it the name as that of the ID
	# It's children are params, declarations, statements
	p[0] = AbstractSyntaxTreeNode("PROCEDURE", [p[4], p[7], p[8]], p[2])
	p[0].vartype = p[1]
	p[0].lineno = p.lineno(1)


# Define parameters
def p_def_parameters(p):
	'''
		params 	: type ID paramslist 
				| type ptr paramslist
				| type addr paramslist
			   	| 
	'''
	if len(p) == 1:
		p[0] = AbstractSyntaxTreeNode("PARAMS", [])
	else:
		# Check for identifiers
		if isinstance(p[2], str):
			p[2] = AbstractSyntaxTreeNode("VAR", [], p[2])

		# Add the variable type.
		p[2].vartype = p[1]
		p[2].lineno = p.lineno(1)
		# p[3] gives a params list, simply add the new parameter to the list in the beginning
		p[0] = p[3]
		p[0].operands.insert(0, p[2])

# def paramslist
def p_def_paramslist(p):
	'''
		paramslist 	: COMMA type ID paramslist
					| COMMA type addr paramslist
					| COMMA type ptr paramslist
					| 
	'''
	if len(p) == 1:
		p[0] = AbstractSyntaxTreeNode("PARAMS", [])
	else:
		if isinstance(p[3], str):
			p[3] = AbstractSyntaxTreeNode("VAR", [], p[3])
		

		# p[4] gives a params list, 
		# simply add the new parameter to the list in the beginning
		p[0] = p[4]
		p[3].vartype = p[2]
		p[3].lineno = p.lineno(1)
		p[0].operands.insert(0, p[3])


# define body (doesn't contain assignments)
def p_def_body(p):
	''' body : body stmt
			 | stmt
	'''
	if len(p) == 2:
		p[0] = AbstractBodyTreeNode("BODY", [p[1]])
	else:
		p[0] = p[1]
		p[0].addChild(p[2])


def p_def_stmt(p):
	''' stmt : assgn SEMICOLON
			 | if_stmt 
			 | while_stmt
			 | function_call
	'''
	p[0] = p[1]


def p_def_function_call(p):
	''' function_call : ID LPAREN opt_params RPAREN SEMICOLON
	'''
	p[0] = AbstractSyntaxTreeNode("FN_CALL", [p[3]] , p[1])

# Optional params to function list
def p_def_opt_params(p):
	''' opt_params  : ID opt_params_list
					| ptr opt_params_list
					| addr opt_params_list
					| 

		opt_params_list : COMMA ID opt_params_list
						| COMMA ptr opt_params_list
						| COMMA addr opt_params_list
						|
	'''
	if len(p) == 1:
		# Base case
		p[0] = AbstractSyntaxTreeNode("OPT_PARAMS", [])
	elif len(p) == 3:
		# opt_params recursion
		if isinstance(p[1], str):
			p[1] = AbstractSyntaxTreeNode("VAR", [], p[1])
		p[0] = p[2]
		p[0].operands.insert(0, p[1])
	else:
		# This is for opt_params_list
		if isinstance(p[2], str):
			p[2] = AbstractSyntaxTreeNode("VAR", [], p[2])
		p[0] = p[3]
		p[0].operands.insert(0, p[2])



# Adding for A3 -> if and while
#############################################################

def p_def_if_stmt(p):
	'''
		if_stmt : IF LPAREN bool_expr RPAREN compound_stmt 				%prec THEN
				| IF LPAREN bool_expr RPAREN compound_stmt ELSE compound_stmt
	'''
	# Only an if-stmt
	if len(p) == 6:
		p[0] = AbstractSyntaxTreeNode("IF", [p[3], p[5]])
	else:
		p[0] = AbstractSyntaxTreeNode("IF", [p[3], p[5], p[7]])
	# cfg_ast.append(p[0])


def p_def_while_stmt(p):
	'''
		while_stmt : WHILE LPAREN bool_expr RPAREN compound_stmt
	'''
	p[0] = AbstractSyntaxTreeNode("WHILE", [p[3], p[5]])
	# cfg_ast.append(p[0])

def p_def_compound_stmt(p):
	'''
		compound_stmt : stmt
					  | SEMICOLON
					  | LCURL RCURL
					  | LCURL body RCURL
	'''
	if len(p) == 2:
		if not isinstance(p[1], str):
			p[0] = AbstractBodyTreeNode("BODY", [p[1]])
		else:
			p[0] = AbstractBodyTreeNode("BODY", [])
	elif len(p) == 3:
		p[0] = AbstractBodyTreeNode("BODY", [])
	else:
		p[0] = p[2]


#############################################################

def p_def_assgn(p):
	''' assgn : ptr_assgn
	 		  | num_assgn
	'''
	p[0] = p[1]


def p_def_decl(p):
	''' decl : type decl_list
	'''
	p[0] = AbstractSyntaxTreeNode("DECL", [p[1], p[2]])



def p_def_decl_list(p):
	''' decl_list : decl_list COMMA ID
				 | decl_list COMMA ptr
				 | ID
				 | ptr
	'''
	if len(p) == 2:
		if not isinstance(p[1], AbstractSyntaxTreeNode):
			p[1] = AbstractSyntaxTreeNode("VAR", [], p[1])
		p[0] = AbstractSyntaxTreeNode("DECL_LIST", [p[1]])
	else:
		if not isinstance(p[3], AbstractSyntaxTreeNode):
			p[3] = AbstractSyntaxTreeNode("VAR", [], p[3])
		p[0] = p[1]
		p[0].addChild(p[3])


def p_def_ptr_assgn(p):
	''' ptr_assgn : ptr EQUALS ptr_expr '''

	p[0] = AbstractSyntaxTreeNode("ASGN", [p[1], p[3]], lineno=p.lineno(1))
	ast_list.append(p[0])

def p_def_num_assgn(p):
	''' num_assgn : ID EQUALS ptr_expr
	'''
	# Allow any expression after a num assignment, except assignments directly to constants
	# Edit: We do this in type-checking
	p[1] = AbstractSyntaxTreeNode("VAR", [], p[1])
	p[0] = AbstractSyntaxTreeNode("ASGN", [p[1], p[3]], lineno=p.lineno(1))
	ast_list.append(p[0])


# This is the boolean expr expression ->
# Precedence order -> || , && , !, (6 comparison ops)
def p_def_bool_expr(p):
	'''	bool_expr : bool_expr OR OR a_bool_expr 
				  | a_bool_expr
	'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = AbstractSyntaxTreeNode("OR", [p[1], p[4]])


def p_def_a_bool_expr(p):
	'''	a_bool_expr : a_bool_expr AND AND n_bool_expr 
				 	| n_bool_expr
	'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = AbstractSyntaxTreeNode("AND", [p[1], p[4]])

def p_def_n_bool_expr(p):
	'''	n_bool_expr : NOT n_bool_expr 
				 | sub_bool_expr
				 | LPAREN bool_expr RPAREN
	'''
	if len(p) == 2:
		p[0] = p[1]
	elif len(p) == 3:
		p[0] = AbstractSyntaxTreeNode("NOT", [p[2]])
	else:
		p[0] = p[2]


# Sub expression that we have
def p_def_sub_bool_expr(p):
	''' sub_bool_expr : ptr_expr GT ptr_expr
					  | ptr_expr GT EQUALS ptr_expr
					  | ptr_expr LT ptr_expr
					  | ptr_expr LT EQUALS ptr_expr
					  | ptr_expr EQUALS EQUALS ptr_expr
					  | ptr_expr NOT EQUALS ptr_expr
	'''
	if len(p) == 4:
		s = "LT" if p[2] == "<" else "GT"
		p[0] = AbstractSyntaxTreeNode(s, [p[1], p[3]])
	else:
		sym = {
			">": "GE",
			"<": "LE",
			"=": "EQ",
			"!": "NE",
		}
		p[0] = AbstractSyntaxTreeNode(sym[p[2]], [p[1], p[4]])


def p_def_ptr_add_expr(p):
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
				| NUMFLOAT
				| ptr
				| addr
				| LPAREN ptr_expr RPAREN
	'''
	if len(p) == 2:
		if isinstance(p[1], str):
			p[1] = AbstractSyntaxTreeNode("VAR", [], p[1])
		elif isinstance(p[1], int):
			p[1] = AbstractSyntaxTreeNode("CONST", [], str(p[1]))
			p[1].vartype = "int"
		elif isinstance(p[1], float):
			p[1] = AbstractSyntaxTreeNode("CONST", [], str(p[1]))
			p[1].vartype = "float"

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
	'''
	if isinstance(p[2], str):
		p[2] = AbstractSyntaxTreeNode("VAR", [],  p[2])

	p[0] = AbstractSyntaxTreeNode("ADDR", [p[2]])



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

	# read input
	with open(filename, 'r') as f:
		data = f.read()

	# ast_file = open(filename + '.ast', 'w')
	# cfg_file = open(filename + '.cfg', 'w')

	lex.input(data)
	yacc.parse(data)

	for c in cfg_ast:
		print(c)

	# Here, we check for errors first. If there are no errors, then we are good to go
	# Print the CFG and ast on 2 different files now
	# error_assignments, messages = check_error_in_assignments(ast_list)
	# if not error_assignments:
	# 	cfg = generateCFG(cfg_ast[0])
	# 	# Write the AST file
	# 	ast_file.write(repr(cfg_ast[0]))
	# 	# Write the CFG file
	# 	cfg_file.write("\n".join([repr(x) for x in cfg]))
	# else:
	# 	for message in messages:
	# 		print(message)

	# ast_file.close()
	# cfg_file.close()
