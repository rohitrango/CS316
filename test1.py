import ply.lex as lex
import ply.yacc as yacc

# List of token names.   This is always required
tokens = (
   'P',
   'T',
   'M',
   'E',
   'D',
   
   'AFACE',
   'ATWO',
   'ARVAL',
   'AHUN',
   'ATHOU',

   'NAME',
   'NUMBER',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'LPAREN',
   'RPAREN',
)


r_values = {
  'twenty'  : 20,
  'thirty'  : 30,
  'fourty'  : 40,
  'fifty'   : 50,
  'sixty'   : 60,
  'seventy' : 70,
  'eighty'  : 80,
  'ninety'  : 90,
}

two_digit_vals = {
  'ten'       : 10,
  'eleven'    : 11,
  'twelve'    : 12, 
  'thirteen'  : 13,
  'fourteen'  : 14,
  'fifteen'   : 15,
  'sixteen'   : 16,
  'seventeen' : 17,
  'eighteen'  : 18,
  'nineteen'  : 19,
}

face_values = {
  'one'     : 1,
  'two'     : 2,
  'three'   : 3,
  'four'    : 4,
  'five'    : 5,
  'six'     : 6,
  'seven'   : 7,
  'eight'   : 8,
  'nine'    : 9,
}

t_AFACE = "(" + "|".join(face_values.keys()) + ")"
t_ARVAL = "(" + "|".join(r_values.keys()) + ")"
t_ATWO  = "(" + "|".join(two_digit_vals.keys()) + ")"
# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'

def t_AHUN(t):
  r'(?i)hundred'
  return t

def t_ATHOU(t):
  r'(?i)thousand'
  return t

def t_P(t):
  r'(?i)plus'
  t.value = "+"
  return t

def t_M(t):
  r'(?i)minus'
  t.value = "-"
  return t

def t_E(t):
  r'(?i)power'
  t.value = "**"
  return t

def t_T(t):
  r'(?i)times'
  t.value = "*"
  return t

def t_D(t):
  r'(?i)divide'
  t.value = "/"
  return t

# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)    
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


precedence = (
  ('left', 'ATHOU'),
  ('left', 'AHUN'),
  ('left', 'AFACE', 'ATWO', 'ARVAL'),
  )

def p_statement_expr(p):
    'statement : expression'
    print(p[1])

def p_thou_group(p):
  '''
    expression : hval ATHOU hval 
            | hval ATHOU dval
            | dval ATHOU hval
            | dval ATHOU dval
            | hval ATHOU 
            | dval ATHOU
            | hval
            | dval
  '''
  print [repr(p[i]) for i in xrange(len(p))]
  if p[1] >= 1000 and len(p)>2:
    raise Exception("Something is wrong.")
    
  if len(p) == 4:
    if p[3] >= 1000:
      raise Exception("Something is wrong.")
    else:
      p[0] = p[1]*1000 + p[3]
  elif len(p) == 3:
      p[0] = p[1]*1000
  else:
      p[0] = p[1]


def p_hval_group(p):
  ''' hval : dval AHUN dval
            | dval AHUN
            | AFACE AHUN dval
  '''
  print [repr(p[i]) for i in xrange(len(p))]
  if len(p) == 4:
    p[0] = p[1]*100 + p[3]
  elif len(p) == 3:
    p[0] = p[1]*100


def p_dval_group(p):
  ''' dval :  ARVAL AFACE
            | ATWO
            | ARVAL
            | AFACE
  '''
  print [repr(p[i]) for i in xrange(len(p))]
  if len(p) == 3:
    p[0] = r_values[p[1]] + face_values[p[2]]
  else:
    if two_digit_vals.has_key(p[1]):
      p[0] = two_digit_vals[p[1]]
    elif r_values.has_key(p[1]):
      p[0] = r_values[p[1]]
    elif face_values.has_key(p[1]):
      p[0] = face_values[p[1]]

def p_error(p):
  if p:
    print("syntax error at {0}".format(p.value))
  else:
    print("syntax error at EOF")


lexer = lex.lex()
yacc.yacc()
# data = "fifty seven hundred twelve "
data = raw_input()
lexer.input(data)
while True:
  tok = lexer.token()
  if not tok:
    break
  print(tok)
yacc.parse(data)