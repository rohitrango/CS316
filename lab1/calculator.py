#!/usr/bin/python3

import sys
import ply.lex as lex
import ply.yacc as yacc
import re

tokens = (
		'P', 'M', 'E', 'T', 'D',
		'NAME', 'NUMBER',
		'PLUS', 'MINUS', 'EXP', 'TIMES', 'DIVIDE', 'EQUALS',
		'LPAREN', 'RPAREN',

		'AFACE',
		'ATWO',
		'ARVAL',
		'AHUN',
		'ATHOU',
)

r_values = {
	'twenty'	: 20,
	'thirty'	: 30,
	'forty'		: 40,
	'fifty'		: 50,
	'sixty'		: 60,
	'seventy'	: 70,
	'eighty'	: 80,
	'ninety'	: 90,
}

two_digit_vals = {
	'ten' 	  	: 10,
	'eleven'	: 11,
	'twelve'	: 12, 
	'thirteen'	: 13,
	'fourteen'	: 14,
	'fifteen'	: 15,
	'sixteen'	: 16,
	'seventeen'	: 17,
	'eighteen'	: 18,
	'nineteen'	: 19,
}

face_values = {
	'one'		: 1,
	'two'		: 2,
	'three'		: 3,
	'four'		: 4,
	'five'		: 5,
	'six'		: 6,
	'seven'		: 7,
	'eight'		: 8,
	'nine'		: 9,
}

t_AFACE = "(" + "|".join(face_values.keys()) + ")(^|\s)"
t_ARVAL = "(" + "|".join(r_values.keys()) + ")(^|\s)"
t_ATWO  = "(" + "|".join(two_digit_vals.keys()) + ")(^|\s)"
t_ignore = " \t\n"

t_PLUS = r'\+'
t_MINUS = r'-'
t_EXP = r'\*\*'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
# t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

def t_NAME(t):
	r'[a-zA-Z_][a-zA-Z0-9_]*'
	s = t.value.lower()
	if s == "hundred":
		t.type = "AHUN"
	if s == "thousand":
		t.type = "ATHOU"
	if r_values.get(s):
		t.type = "ARVAL"
	if face_values.get(s):
		t.type = "AFACE"
	if two_digit_vals.get(s):
		t.type = "ATWO"
	if s == "plus":
		t.type = "P"
		t.value = "+"
	if s == "minus":
		t.type = "M"
		t.value = "-"
	if s == "times":
		t.type = "T"
		t.value = "*"
	if s == "divide":
		t.type = "D"
		t.value = "/"
	if s == "power":
		t.type = "E"
		t.value = "**"

	return t


def t_AHUN(t):
  r'(?i)hundred(^|\s)'
  return t

def t_ATHOU(t):
  r'(?i)thousand(^|\s)'
  return t

def t_P(t):
  r'(?i)plus(^|\s)'
  t.value = "+"
  return t

def t_M(t):
  r'(?i)minus(^|\s)'
  t.value = "-"
  return t

def t_E(t):
  r'(?i)power(^|\s)'
  t.value = "**"
  return t

def t_T(t):
  r'(?i)times(^|\s)'
  t.value = "*"
  return t

def t_D(t):
  r'(?i)divide(^|\s)'
  t.value = "/"
  return t

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
		('left', 'PLUS', 'P', 'MINUS', 'M'),
		('left', 'TIMES', 'T', 'DIVIDE', 'D'),
		('left', 'EXP', 'E'),
		('right', 'UMINUS'),
		('left', 'ATHOU'),
		('left', 'AHUN'),
		('left', 'AFACE', 'ATWO', 'ARVAL'),
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
				  | expression P expression
				  | expression M expression
				  | expression T expression
				  | expression D expression
				  | expression E expression
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
		'''expression : MINUS expression
					 	| M expression  %prec UMINUS'''
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

def p_thou_group(p):
  '''
    expression :  dval ATHOU hval
            | dval ATHOU dval
			| dval ATHOU af

            | af ATHOU hval
            | af ATHOU dval
			| af ATHOU af

            | dval ATHOU
            | af ATHOU

            | hval
            | dval
            | af
  '''
  # print([repr(p[i]) for i in range(len(p))])   
  if len(p) == 4:
      p[0] = p[1]*1000 + p[3]
  elif len(p) == 3:
      p[0] = p[1]*1000
  else:
      p[0] = p[1]

# def p_hhval_group(p):
#   ''' hhval : dval AHUN dval
#   			| dval AHUN af
#             | dval AHUN
#   '''
#   if p[1] == 10:
#   	raise Exception("ten hundred isn't valid.")
#   # print [repr(p[i]) for i in range(len(p))]
#   if len(p) == 4:
#     p[0] = p[1]*100 + p[3]
#   elif len(p) == 3:
#     p[0] = p[1]*100

def p_hval_group(p):
	''' hval : af AHUN dval
			 | af AHUN af
			 | af AHUN
	'''
	# print([repr(p[i]) for i in range(len(p))])
	if len(p) == 4:
		p[0] = p[1]*100 + p[3]
	else:
		p[0] = p[1]*100


def p_dval_group(p):
  ''' dval :  ARVAL af
            | ARVAL
            | ATWO
  '''
  # print [repr(p[i]) for i in range(len(p))]
  p[1] = p[1].strip(" ").strip("\n")
  if len(p) == 3:
    p[0] = r_values[p[1]] + p[2]
  else:
    if two_digit_vals.get(p[1]):
      p[0] = two_digit_vals[p[1]]
    elif r_values.get(p[1]):
      p[0] = r_values[p[1]]

def p_af_group(p):
	''' af : AFACE
	'''
	p[0] = face_values[p[1].strip(" ").strip("\n")]

def p_error(p):
	if p:
		print("syntax error at {0}".format(p.value))
	else:
		print("syntax error at EOF")
	sys.exit(0)

def process(data):
	lex.lex()
	# lex.input(data)
	# while True:
	# 	tok = lex.token()
	# 	if not tok:
	# 		break
	# 	print(tok)
	yacc.yacc()
	yacc.parse(data)

if __name__ == "__main__":
	print("Enter the Equation")
	data = sys.stdin.readline().lower()
	process(data)
