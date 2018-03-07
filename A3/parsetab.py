
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'leftTHENleftELSEleftPLUSMINUSleftSTARSLASHrightUMINUSID STAR AND NUM LPAREN RPAREN COMMA LCURL RCURL SEMICOLON EQUALS PLUS MINUS SLASH LT GT NOT OR INT VOID ELSE WHILE MAIN IF prog : VOID MAIN LPAREN RPAREN LCURL body RCURL\n\t\t\t | VOID MAIN LPAREN RPAREN LCURL RCURL\n\t body : body stmt\n\t\t\t | stmt\n\t stmt : decl SEMICOLON \n\t\t\t | assgn SEMICOLON\n\t\t\t | if_stmt \n\t\t\t | while_stmt\n\t\n\t\tif_stmt : IF LPAREN bool_expr RPAREN compound_stmt \t\t\t\t%prec THEN\n\t\t\t\t| IF LPAREN bool_expr RPAREN compound_stmt ELSE compound_stmt\n\t\n\t\twhile_stmt : WHILE LPAREN bool_expr RPAREN compound_stmt\n\t\n\t\tcompound_stmt : stmt\n\t\t\t\t\t  | LCURL body RCURL\n\t assgn : ptr_assgn\n\t \t\t  | num_assgn\n\t decl : INT decl_list\n\t decl_list : decl_list COMMA ID\n\t\t\t\t | decl_list COMMA ptr\n\t\t\t\t | ID\n\t\t\t\t | ptr\n\t ptr_assgn : ptr EQUALS ptr_expr  num_assgn : ID EQUALS ptr_expr\n\t\tbool_expr : bool_expr OR OR a_bool_expr \n\t\t\t\t  | a_bool_expr\n\t\ta_bool_expr : a_bool_expr AND AND n_bool_expr \n\t\t\t\t \t| n_bool_expr\n\t\tn_bool_expr : NOT n_bool_expr \n\t\t\t\t | sub_bool_expr\n\t sub_bool_expr : ptr_expr GT ptr_expr\n\t\t\t\t\t  | ptr_expr GT EQUALS ptr_expr\n\t\t\t\t\t  | ptr_expr LT ptr_expr\n\t\t\t\t\t  | ptr_expr LT EQUALS ptr_expr\n\t\t\t\t\t  | ptr_expr EQUALS EQUALS ptr_expr\n\t\t\t\t\t  | ptr_expr NOT EQUALS ptr_expr\n\t\tptr_expr : ptr_expr PLUS ptr_factor \n\t\t\t\t | ptr_expr MINUS ptr_factor\n\t\t\t\t | ptr_factor\n\t\n\t\tptr_factor :  ptr_factor STAR ptr_term\n\t\t\t\t \t| ptr_factor SLASH ptr_term\n\t\t\t\t \t| ptr_term\n\t ptr_term :  MINUS ptr_term  \t\t%prec UMINUS\n\t\t\t\t  | ptr_expr_base\n\t ptr_expr_base : ID\n\t\t\t\t| NUM\n\t\t\t\t| ptr\n\t\t\t\t| addr\n\t\t\t\t| LPAREN ptr_expr RPAREN\n\t  ptr : STAR ptr \n\t\t\t | STAR ID\n\t\t\t | STAR addr\n\t addr : AND ID\n\t\t\t | AND ptr\n\t\t\t | AND addr\n\t'
    
_lr_action_items = {'STAR':([6,8,13,15,18,19,21,22,23,24,25,26,27,28,29,31,32,33,37,38,39,40,42,44,45,46,47,48,49,52,54,58,61,62,63,64,66,68,69,71,73,76,77,78,79,80,81,82,83,84,86,87,89,90,91,92,94,100,101,102,],[8,8,8,-4,-7,8,-8,-5,8,-50,-48,-49,8,8,-6,-3,8,8,-53,-51,-52,8,-40,61,8,-46,-45,-42,-44,-43,8,8,8,8,-41,8,8,8,8,8,8,-47,8,-38,-39,8,-11,-12,8,8,8,8,61,8,61,-9,8,8,-13,-10,]),'LPAREN':([3,9,17,27,28,32,33,40,45,54,61,62,66,68,69,71,77,83,84,86,87,90,],[4,27,33,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,]),'VOID':([0,],[1,]),'WHILE':([6,13,15,18,21,22,29,31,64,73,80,81,82,92,94,100,101,102,],[9,9,-4,-7,-8,-5,-6,-3,9,9,9,-11,-12,-9,9,9,-13,-10,]),'MINUS':([24,25,26,27,28,32,33,37,38,39,40,42,44,45,46,47,48,49,51,52,54,55,56,59,61,62,63,66,68,69,71,76,77,78,79,83,84,85,86,87,88,89,90,91,96,97,98,99,],[-50,-48,-49,45,45,45,45,-53,-51,-52,45,-40,-37,45,-46,-45,-42,-44,71,-43,45,71,71,71,45,45,-41,45,45,45,45,-47,45,-38,-39,45,45,71,45,45,71,-35,45,-36,71,71,71,71,]),'LCURL':([5,64,73,100,],[6,80,80,80,]),'RPAREN':([4,24,25,26,37,38,39,41,42,43,44,46,47,48,49,50,52,53,57,59,63,72,76,78,79,85,88,89,91,93,95,96,97,98,99,],[5,-50,-48,-49,-53,-51,-52,-28,-40,-24,-37,-46,-45,-42,-44,64,-43,-26,73,76,-41,-27,-47,-38,-39,-29,-31,-35,-36,-25,-23,-30,-33,-32,-34,]),'SEMICOLON':([7,11,14,20,24,25,26,34,35,36,37,38,39,42,44,46,47,48,49,52,55,56,63,74,75,76,78,79,89,91,],[22,29,-15,-14,-50,-48,-49,-16,-20,-19,-53,-51,-52,-40,-37,-46,-45,-42,-44,-43,-21,-22,-41,-18,-17,-47,-38,-39,-35,-36,]),'RCURL':([6,13,15,18,21,22,29,31,81,82,92,94,101,102,],[12,30,-4,-7,-8,-5,-6,-3,-11,-12,-9,101,-13,-10,]),'LT':([24,25,26,37,38,39,42,44,46,47,48,49,51,52,63,76,78,79,89,91,],[-50,-48,-49,-53,-51,-52,-40,-37,-46,-45,-42,-44,68,-43,-41,-47,-38,-39,-35,-36,]),'NUM':([27,28,32,33,40,45,54,61,62,66,68,69,71,77,83,84,86,87,90,],[49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,]),'PLUS':([24,25,26,37,38,39,42,44,46,47,48,49,51,52,55,56,59,63,76,78,79,85,88,89,91,96,97,98,99,],[-50,-48,-49,-53,-51,-52,-40,-37,-46,-45,-42,-44,69,-43,69,69,69,-41,-47,-38,-39,69,69,-35,-36,69,69,69,69,]),'COMMA':([24,25,26,34,35,36,37,38,39,74,75,],[-50,-48,-49,58,-20,-19,-53,-51,-52,-18,-17,]),'$end':([2,12,30,],[0,-2,-1,]),'GT':([24,25,26,37,38,39,42,44,46,47,48,49,51,52,63,76,78,79,89,91,],[-50,-48,-49,-53,-51,-52,-40,-37,-46,-45,-42,-44,66,-43,-41,-47,-38,-39,-35,-36,]),'EQUALS':([10,16,24,25,26,37,38,39,42,44,46,47,48,49,51,52,63,66,67,68,70,76,78,79,89,91,],[28,32,-50,-48,-49,-53,-51,-52,-40,-37,-46,-45,-42,-44,67,-43,-41,84,86,87,90,-47,-38,-39,-35,-36,]),'ELSE':([18,21,22,29,81,82,92,101,102,],[-7,-8,-5,-6,-11,-12,100,-13,-10,]),'SLASH':([24,25,26,37,38,39,42,44,46,47,48,49,52,63,76,78,79,89,91,],[-50,-48,-49,-53,-51,-52,-40,62,-46,-45,-42,-44,-43,-41,-47,-38,-39,62,62,]),'ID':([6,8,13,15,18,19,21,22,23,27,28,29,31,32,33,40,45,54,58,61,62,64,66,68,69,71,73,77,80,81,82,83,84,86,87,90,92,94,100,101,102,],[16,26,16,-4,-7,36,-8,-5,38,52,52,-6,-3,52,52,52,52,52,75,52,52,16,52,52,52,52,16,52,16,-11,-12,52,52,52,52,52,-9,16,16,-13,-10,]),'IF':([6,13,15,18,21,22,29,31,64,73,80,81,82,92,94,100,101,102,],[17,17,-4,-7,-8,-5,-6,-3,17,17,17,-11,-12,-9,17,17,-13,-10,]),'AND':([8,23,24,25,26,27,28,32,33,37,38,39,40,41,42,43,44,45,46,47,48,49,52,53,54,60,61,62,63,66,68,69,71,72,76,77,78,79,83,84,85,86,87,88,89,90,91,93,95,96,97,98,99,],[23,23,-50,-48,-49,23,23,23,23,-53,-51,-52,23,-28,-40,60,-37,23,-46,-45,-42,-44,-43,-26,23,77,23,23,-41,23,23,23,23,-27,-47,23,-38,-39,23,23,-29,23,23,-31,-35,23,-36,-25,60,-30,-33,-32,-34,]),'INT':([6,13,15,18,21,22,29,31,64,73,80,81,82,92,94,100,101,102,],[19,19,-4,-7,-8,-5,-6,-3,19,19,19,-11,-12,-9,19,19,-13,-10,]),'NOT':([24,25,26,27,33,37,38,39,42,44,46,47,48,49,51,52,54,63,76,77,78,79,83,89,91,],[-50,-48,-49,54,54,-53,-51,-52,-40,-37,-46,-45,-42,-44,70,-43,54,-41,-47,54,-38,-39,54,-35,-36,]),'MAIN':([1,],[3,]),'OR':([24,25,26,37,38,39,41,42,43,44,46,47,48,49,50,52,53,57,63,65,72,76,78,79,85,88,89,91,93,95,96,97,98,99,],[-50,-48,-49,-53,-51,-52,-28,-40,-24,-37,-46,-45,-42,-44,65,-43,-26,65,-41,83,-27,-47,-38,-39,-29,-31,-35,-36,-25,-23,-30,-33,-32,-34,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'body':([6,80,],[13,94,]),'decl':([6,13,64,73,80,94,100,],[7,7,7,7,7,7,7,]),'n_bool_expr':([27,33,54,77,83,],[53,53,72,93,53,]),'a_bool_expr':([27,33,83,],[43,43,95,]),'if_stmt':([6,13,64,73,80,94,100,],[18,18,18,18,18,18,18,]),'assgn':([6,13,64,73,80,94,100,],[11,11,11,11,11,11,11,]),'num_assgn':([6,13,64,73,80,94,100,],[14,14,14,14,14,14,14,]),'ptr_assgn':([6,13,64,73,80,94,100,],[20,20,20,20,20,20,20,]),'bool_expr':([27,33,],[50,57,]),'sub_bool_expr':([27,33,54,77,83,],[41,41,41,41,41,]),'stmt':([6,13,64,73,80,94,100,],[15,31,82,82,15,31,82,]),'ptr_term':([27,28,32,33,40,45,54,61,62,66,68,69,71,77,83,84,86,87,90,],[42,42,42,42,42,63,42,78,79,42,42,42,42,42,42,42,42,42,42,]),'ptr_expr_base':([27,28,32,33,40,45,54,61,62,66,68,69,71,77,83,84,86,87,90,],[48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,]),'while_stmt':([6,13,64,73,80,94,100,],[21,21,21,21,21,21,21,]),'decl_list':([19,],[34,]),'compound_stmt':([64,73,100,],[81,92,102,]),'prog':([0,],[2,]),'ptr_factor':([27,28,32,33,40,54,66,68,69,71,77,83,84,86,87,90,],[44,44,44,44,44,44,44,44,89,91,44,44,44,44,44,44,]),'ptr_expr':([27,28,32,33,40,54,66,68,77,83,84,86,87,90,],[51,55,56,51,59,51,85,88,51,51,96,97,98,99,]),'ptr':([6,8,13,19,23,27,28,32,33,40,45,54,58,61,62,64,66,68,69,71,73,77,80,83,84,86,87,90,94,100,],[10,25,10,35,39,47,47,47,47,47,47,47,74,47,47,10,47,47,47,47,10,47,10,47,47,47,47,47,10,10,]),'addr':([8,23,27,28,32,33,40,45,54,61,62,66,68,69,71,77,83,84,86,87,90,],[24,37,46,46,46,46,46,46,46,46,46,46,46,46,46,46,46,46,46,46,46,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> prog","S'",1,None,None,None),
  ('prog -> VOID MAIN LPAREN RPAREN LCURL body RCURL','prog',7,'p_def_prog','150050061_17V051001.py',137),
  ('prog -> VOID MAIN LPAREN RPAREN LCURL RCURL','prog',6,'p_def_prog','150050061_17V051001.py',138),
  ('body -> body stmt','body',2,'p_def_body','150050061_17V051001.py',147),
  ('body -> stmt','body',1,'p_def_body','150050061_17V051001.py',148),
  ('stmt -> decl SEMICOLON','stmt',2,'p_def_stmt','150050061_17V051001.py',158),
  ('stmt -> assgn SEMICOLON','stmt',2,'p_def_stmt','150050061_17V051001.py',159),
  ('stmt -> if_stmt','stmt',1,'p_def_stmt','150050061_17V051001.py',160),
  ('stmt -> while_stmt','stmt',1,'p_def_stmt','150050061_17V051001.py',161),
  ('if_stmt -> IF LPAREN bool_expr RPAREN compound_stmt','if_stmt',5,'p_def_if_stmt','150050061_17V051001.py',171),
  ('if_stmt -> IF LPAREN bool_expr RPAREN compound_stmt ELSE compound_stmt','if_stmt',7,'p_def_if_stmt','150050061_17V051001.py',172),
  ('while_stmt -> WHILE LPAREN bool_expr RPAREN compound_stmt','while_stmt',5,'p_def_while_stmt','150050061_17V051001.py',184),
  ('compound_stmt -> stmt','compound_stmt',1,'p_def_compound_stmt','150050061_17V051001.py',191),
  ('compound_stmt -> LCURL body RCURL','compound_stmt',3,'p_def_compound_stmt','150050061_17V051001.py',192),
  ('assgn -> ptr_assgn','assgn',1,'p_def_assgn','150050061_17V051001.py',203),
  ('assgn -> num_assgn','assgn',1,'p_def_assgn','150050061_17V051001.py',204),
  ('decl -> INT decl_list','decl',2,'p_def_decl','150050061_17V051001.py',210),
  ('decl_list -> decl_list COMMA ID','decl_list',3,'p_def_decl_list','150050061_17V051001.py',217),
  ('decl_list -> decl_list COMMA ptr','decl_list',3,'p_def_decl_list','150050061_17V051001.py',218),
  ('decl_list -> ID','decl_list',1,'p_def_decl_list','150050061_17V051001.py',219),
  ('decl_list -> ptr','decl_list',1,'p_def_decl_list','150050061_17V051001.py',220),
  ('ptr_assgn -> ptr EQUALS ptr_expr','ptr_assgn',3,'p_def_ptr_assgn','150050061_17V051001.py',230),
  ('num_assgn -> ID EQUALS ptr_expr','num_assgn',3,'p_def_num_assgn','150050061_17V051001.py',236),
  ('bool_expr -> bool_expr OR OR a_bool_expr','bool_expr',4,'p_def_bool_expr','150050061_17V051001.py',252),
  ('bool_expr -> a_bool_expr','bool_expr',1,'p_def_bool_expr','150050061_17V051001.py',253),
  ('a_bool_expr -> a_bool_expr AND AND n_bool_expr','a_bool_expr',4,'p_def_a_bool_expr','150050061_17V051001.py',262),
  ('a_bool_expr -> n_bool_expr','a_bool_expr',1,'p_def_a_bool_expr','150050061_17V051001.py',263),
  ('n_bool_expr -> NOT n_bool_expr','n_bool_expr',2,'p_def_n_bool_expr','150050061_17V051001.py',271),
  ('n_bool_expr -> sub_bool_expr','n_bool_expr',1,'p_def_n_bool_expr','150050061_17V051001.py',272),
  ('sub_bool_expr -> ptr_expr GT ptr_expr','sub_bool_expr',3,'p_def_sub_bool_expr','150050061_17V051001.py',282),
  ('sub_bool_expr -> ptr_expr GT EQUALS ptr_expr','sub_bool_expr',4,'p_def_sub_bool_expr','150050061_17V051001.py',283),
  ('sub_bool_expr -> ptr_expr LT ptr_expr','sub_bool_expr',3,'p_def_sub_bool_expr','150050061_17V051001.py',284),
  ('sub_bool_expr -> ptr_expr LT EQUALS ptr_expr','sub_bool_expr',4,'p_def_sub_bool_expr','150050061_17V051001.py',285),
  ('sub_bool_expr -> ptr_expr EQUALS EQUALS ptr_expr','sub_bool_expr',4,'p_def_sub_bool_expr','150050061_17V051001.py',286),
  ('sub_bool_expr -> ptr_expr NOT EQUALS ptr_expr','sub_bool_expr',4,'p_def_sub_bool_expr','150050061_17V051001.py',287),
  ('ptr_expr -> ptr_expr PLUS ptr_factor','ptr_expr',3,'p_def_ptr_add_expr','150050061_17V051001.py',303),
  ('ptr_expr -> ptr_expr MINUS ptr_factor','ptr_expr',3,'p_def_ptr_add_expr','150050061_17V051001.py',304),
  ('ptr_expr -> ptr_factor','ptr_expr',1,'p_def_ptr_add_expr','150050061_17V051001.py',305),
  ('ptr_factor -> ptr_factor STAR ptr_term','ptr_factor',3,'p_def_ptr_factor','150050061_17V051001.py',319),
  ('ptr_factor -> ptr_factor SLASH ptr_term','ptr_factor',3,'p_def_ptr_factor','150050061_17V051001.py',320),
  ('ptr_factor -> ptr_term','ptr_factor',1,'p_def_ptr_factor','150050061_17V051001.py',321),
  ('ptr_term -> MINUS ptr_term','ptr_term',2,'p_def_ptr_term','150050061_17V051001.py',334),
  ('ptr_term -> ptr_expr_base','ptr_term',1,'p_def_ptr_term','150050061_17V051001.py',335),
  ('ptr_expr_base -> ID','ptr_expr_base',1,'p_def_ptr_expr_base','150050061_17V051001.py',344),
  ('ptr_expr_base -> NUM','ptr_expr_base',1,'p_def_ptr_expr_base','150050061_17V051001.py',345),
  ('ptr_expr_base -> ptr','ptr_expr_base',1,'p_def_ptr_expr_base','150050061_17V051001.py',346),
  ('ptr_expr_base -> addr','ptr_expr_base',1,'p_def_ptr_expr_base','150050061_17V051001.py',347),
  ('ptr_expr_base -> LPAREN ptr_expr RPAREN','ptr_expr_base',3,'p_def_ptr_expr_base','150050061_17V051001.py',348),
  ('ptr -> STAR ptr','ptr',2,'p_def_ptr','150050061_17V051001.py',364),
  ('ptr -> STAR ID','ptr',2,'p_def_ptr','150050061_17V051001.py',365),
  ('ptr -> STAR addr','ptr',2,'p_def_ptr','150050061_17V051001.py',366),
  ('addr -> AND ID','addr',2,'p_def_addr','150050061_17V051001.py',375),
  ('addr -> AND ptr','addr',2,'p_def_addr','150050061_17V051001.py',376),
  ('addr -> AND addr','addr',2,'p_def_addr','150050061_17V051001.py',377),
]
