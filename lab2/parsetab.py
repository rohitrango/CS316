
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'ID STAR AND NUM LPAREN RPAREN COMMA LCURL RCURL SEMICOLON EQUALS INT VOID MAIN prog : VOID MAIN LPAREN RPAREN LCURL body RCURL\n\t body : stmt body\n\t\t\t | stmt\n\t stmt : expr1 SEMICOLON \n\t\t\t | expr2 SEMICOLON\n\t expr2 : expr2 COMMA equality \n\t\t\t  | equality \n\t equality : equality1\n\t \t\t\t | equality2\n\t expr1 : INT subexpr1\n\t subexpr1 : subexpr1 COMMA ID\n\t\t\t\t | subexpr1 COMMA ptr\n\t\t\t\t | subexpr1 COMMA equality1\n\t\t\t\t | ID\n\t\t\t\t | ptr\n\t\t\t\t | equality1\n\t equality1 : ptr EQUALS ptrexpr  equality2 : ID EQUALS addr  ptrexpr : ptr EQUALS ptrexpr\n\t\t\t\t| NUM\n\t\t\t\t| ptr\n\t\t\t\t| addr\n\t  ptr : STAR ID\n\t addr : AND ID\n\t'
    
_lr_action_items = {'AND':([19,25,39,],[30,30,30,]),'RPAREN':([4,],[5,]),'SEMICOLON':([9,10,14,16,17,18,26,27,28,29,31,32,33,34,35,36,38,40,41,42,43,],[21,22,-7,-8,-9,-23,-10,-15,-16,-14,-22,-17,-20,-21,-6,-18,-24,-12,-13,-11,-19,]),'INT':([6,12,21,22,],[15,15,-5,-4,]),'VOID':([0,],[1,]),'EQUALS':([8,13,18,27,34,40,],[19,25,-23,19,39,19,]),'ID':([6,7,12,15,20,21,22,30,37,],[13,18,13,29,13,-5,-4,38,42,]),'RCURL':([11,12,21,22,24,],[23,-3,-5,-4,-2,]),'NUM':([19,39,],[33,33,]),'COMMA':([9,14,16,17,18,26,27,28,29,31,32,33,34,35,36,38,40,41,42,43,],[20,-7,-8,-9,-23,37,-15,-16,-14,-22,-17,-20,-21,-6,-18,-24,-12,-13,-11,-19,]),'LPAREN':([3,],[4,]),'STAR':([6,12,15,19,20,21,22,37,39,],[7,7,7,7,7,-5,-4,7,7,]),'MAIN':([1,],[3,]),'$end':([2,23,],[0,-1,]),'LCURL':([5,],[6,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'body':([6,12,],[11,24,]),'equality':([6,12,20,],[14,14,35,]),'addr':([19,25,39,],[31,36,31,]),'ptrexpr':([19,39,],[32,43,]),'subexpr1':([15,],[26,]),'stmt':([6,12,],[12,12,]),'expr2':([6,12,],[9,9,]),'expr1':([6,12,],[10,10,]),'prog':([0,],[2,]),'equality1':([6,12,15,20,37,],[16,16,28,16,41,]),'ptr':([6,12,15,19,20,37,39,],[8,8,27,34,8,40,34,]),'equality2':([6,12,20,],[17,17,17,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> prog","S'",1,None,None,None),
  ('prog -> VOID MAIN LPAREN RPAREN LCURL body RCURL','prog',7,'p_def_prog','lab2.py',55),
  ('body -> stmt body','body',2,'p_def_body','lab2.py',61),
  ('body -> stmt','body',1,'p_def_body','lab2.py',62),
  ('stmt -> expr1 SEMICOLON','stmt',2,'p_def_stmt','lab2.py',67),
  ('stmt -> expr2 SEMICOLON','stmt',2,'p_def_stmt','lab2.py',68),
  ('expr2 -> expr2 COMMA equality','expr2',3,'p_def_expr2','lab2.py',73),
  ('expr2 -> equality','expr2',1,'p_def_expr2','lab2.py',74),
  ('equality -> equality1','equality',1,'p_def_equality','lab2.py',79),
  ('equality -> equality2','equality',1,'p_def_equality','lab2.py',80),
  ('expr1 -> INT subexpr1','expr1',2,'p_def_expr1','lab2.py',85),
  ('subexpr1 -> subexpr1 COMMA ID','subexpr1',3,'p_def_subexpr1','lab2.py',90),
  ('subexpr1 -> subexpr1 COMMA ptr','subexpr1',3,'p_def_subexpr1','lab2.py',91),
  ('subexpr1 -> subexpr1 COMMA equality1','subexpr1',3,'p_def_subexpr1','lab2.py',92),
  ('subexpr1 -> ID','subexpr1',1,'p_def_subexpr1','lab2.py',93),
  ('subexpr1 -> ptr','subexpr1',1,'p_def_subexpr1','lab2.py',94),
  ('subexpr1 -> equality1','subexpr1',1,'p_def_subexpr1','lab2.py',95),
  ('equality1 -> ptr EQUALS ptrexpr','equality1',3,'p_def_equality1','lab2.py',108),
  ('equality2 -> ID EQUALS addr','equality2',3,'p_def_equality2','lab2.py',115),
  ('ptrexpr -> ptr EQUALS ptrexpr','ptrexpr',3,'p_def_ptrexpr','lab2.py',121),
  ('ptrexpr -> NUM','ptrexpr',1,'p_def_ptrexpr','lab2.py',122),
  ('ptrexpr -> ptr','ptrexpr',1,'p_def_ptrexpr','lab2.py',123),
  ('ptrexpr -> addr','ptrexpr',1,'p_def_ptrexpr','lab2.py',124),
  ('ptr -> STAR ID','ptr',2,'p_def_ptr','lab2.py',135),
  ('addr -> AND ID','addr',2,'p_def_addr','lab2.py',141),
]
