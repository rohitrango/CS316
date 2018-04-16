'''
-----------------------------------------------------------------------
Data Structure for Abstract Syntax Tree
-----------------------------------------------------------------------
'''
from copy import deepcopy
import inspect

sym_to_name_mapping = {
	'PLUS'	: '+',
	'MINUS'	: '-',
	'DIV' 	: '/',
	'MUL'	: '*',
	'UMINUS': '-',
}

bool_to_name_mapping = {
	'LT'	: '<',
	'GT'	: '>',
	'LE'	: '<=',
	'GE'	: '>=',
	'NE'	: '!=',
	'EQ'	: '==',
	'AND'	: '&&',
	'OR'	: '||',
	'NOT'	: '!',
}

class AbstractSyntaxTreeNode(object):

	def __init__(self, operator, operands=[], name=None, lineno=None, vartype=None, lvl=0, tmp=False):
		'''
		operator : It's the operator of the AST node e.g. PLUS, VAR, DECL
		operands : The list of operands to apply the operator on. 
		name  	 : Specific name in case of variables, constants, etc.
		lineno 	 : The lineno. of the piece of code taken while parsing.
		vartype  : Default : None. Only applicable for arguments inside the parameter.
					Also, set it to 'int' or 'float' for CONST types
		'''
		self.operator = operator
		self.name = name
		self.operands = operands
		self.lineno = lineno
		self.vartype = vartype
		self.lvl = lvl
		self.tmp = tmp

	def addChild(self, child):
		self.operands.append(child)

	def __repr__(self, depth=0):
		# Do something special for function call
		if self.operator == "FN_CALL":
			paramsStr = ("\n" + (depth+1)*"\t" + ",\n").join(map(lambda x: x.__repr__(depth+1), self.operands)) + "\n"
			if len(paramsStr) == 1:
				paramsStr = ""

			return depth*"\t" + "CALL " + self.name + "(\n" \
					+ paramsStr + depth*"\t" + ")"


		if len(self.operands) == 0:
			if self.operator == "RETURN":
				return depth*"\t" + self.operator + "\n" + depth*"\t" + "(\n" + depth*"\t" + ")"
			else:
				return depth*"\t" + self.operator + "(" + str(self.name) + ")"

			# if self.operator in ["VAR", "CONST", "TYPE"]:
			# 	return depth*"\t" + self.operator + "(" + str(self.name) + ")"
			# else:
			# 	return depth*"\t" + ""

		else:
			return depth*"\t" + self.operator + "\n" + depth*"\t" + "(\n" \
					+ ("\n" + (depth+1)*"\t" + ",\n").join(map(lambda x: x.__repr__(depth+1), self.operands)) + "\n" + depth*"\t" + ")" 

	# Check if the expression is a constant or not
	def isConst(self):
		if len(self.operands) == 0:
			return self.operator == "CONST"
		else:
			return all(x.isConst() for x in self.operands)

	# This function gives the CFG printable equivalent
	# Change this as you wish
	def printable(self):
		if self.operator == "ASGN":
			return self.operands[0].printable() + " = " + self.operands[1].printable()
		elif self.operator in ["VAR", "CONST"]:
			return self.name
		elif self.operator == "ADDR":
			return "&" + self.operands[0].printable()
		elif self.operator == "RETURN":
			return "return " + "".join(map(lambda x: x.printable(), self.operands))
		elif self.operator == "DEREF":
			return "*" + self.operands[0].printable()
		elif self.operator in sym_to_name_mapping.keys():
			# Take care of UMINUS
			# print(self.operator, len(self.operands))
			if len(self.operands) == 1:
				return "-" + self.operands[0].printable()
			else:
				return self.operands[0].printable() + " " + sym_to_name_mapping[self.operator] + " " + self.operands[1].printable()

		elif self.operator in bool_to_name_mapping.keys():
			if self.operator == "NOT":
				return "!" + self.operands[0].printable()
			else:
				return self.operands[0].printable() + " " + bool_to_name_mapping[self.operator] + " " + self.operands[1].printable()
		# Function calls
		elif self.operator == "FN_CALL":
			stmt = "*"*self.lvl + self.name + "(" + ", ".join(map(lambda x: x.printable(), self.operands[0].operands)) + ")"
			return stmt

		else:
			print(self)
			raise Exception


# This is for body statements since they are printed differently in the reference implementation
class AbstractBodyTreeNode(AbstractSyntaxTreeNode):
	def __init__(self, operator, operands=[], name=None):
		super(AbstractBodyTreeNode, self).__init__(operator, operands, name)

	def __repr__(self, depth=0):
		res = ""
		children = [child for child in self.operands if child.operator!="DECL"]
		if self.operator == "BODY":
			res += "\n".join([child.__repr__(depth=depth) for child in children])
		else:
			res += ("\n"+"\t"*depth+",\n").join([child.__repr__(depth=depth) for child in children])
		return res

# This function will help to check for errors in the assignments of the AST
# This will be extended to type-checking later
# def check_error_in_assignments(ast_list):
# 	flag = False
# 	messages = []
# 	# For every assignment, check if LHS is var, and RHS is const
# 	for asgn in ast_list:
# 		if (asgn.operands[0].operator=="VAR" and asgn.operands[1].isConst()):
# 			flag = True
# 			messages.append("Syntax error: Static assignments to constants not allowed, line no. {0}".format(asgn.lineno))
# 			break

# 	return flag, messages


#########################################
## Block class
#########################################
class Block(object):

	def __init__(self, number, contents=[], goto=None, goto2=None, end=False):
		self.goto = goto
		self.goto2 = goto2
		self.number = number
		self.contents = contents
		self.end = end

	def addStmts(self, stmts):
		# Assuming that stmts is a list
		if isinstance(stmts, list):
			self.contents.extend(stmts)
		else:
			# Shouldn't occur
			raise NotImplementedError

	def __repr__(self):
		string = "<bb " + str(self.number) + ">"
		# Check if it's the end block
		for op in self.contents:
			string += ("\n" + op.printable())
		if not self.end:
			if self.goto2 is None:
				string += ("\ngoto <bb " + str(self.goto) + ">")
			else:
				string += ("\nif(" + self.contents[-1].printable().split(" ")[0] + ") goto <bb " + str(self.goto) + ">")
				string += ("\nelse goto <bb " + str(self.goto2) + ">")
		return string + "\n"

'''
Class for FunctionBlockContainer
This contains a neat (not-so-neat) format for printing the blocks corresponding to a function and its params
'''
class FunctionBlockContainer(object):
	def __init__(self, package):
		self.name   = package['name']
		self.blocks = package['blocks']
		self.params = package['params']

	def __repr__(self):
		stmt = "function {0}({1})\n".format(self.name, self.params)
		for blk in self.blocks:
			stmt += blk.__repr__() + "\n"
		return stmt



def getProcedureCFGs(proceduresAST):
	'''
	Take a list of procedures and return a list of blocks for each CFG
	params : proceduresAST   - the list of procedures 
	returns: procedureCFGs   - list of CFGs for each procedure in order of defintion
	'''
	bb_ctr, t_ctr = 1, 0
	procedureCFGs = []
	for func in proceduresAST.operands:
		params, decl, body = func.operands
		blkList, bb_ctr, t_ctr = generateFunctionCFG(body, bb_ctr, t_ctr)
		procedureCFGs.append(FunctionBlockContainer({
			'blocks' : blkList,
			'name'   : func.name.name,
			'params' : getParamsHeader(params),
			}))
	return procedureCFGs

# generate the CFG given a node
def generateFunctionCFG(node, bb_ctr=1, t_ctr=0):
	'''
	generate CFG for a particular function

	params : node   - AST for the body of the function
			 bb_ctr - First usable Block number
			 t_ctr  - First usable tmp variable number

	returns: block_list - get the block list
			 bb_ctr     - Next usable block number
			 t_ctr   	- Next usable tmp number

	'''
	neg_ctr = -1

	# Sub-Master code. Keep a list of block iterms along with the current block. As you keep getting more statements,
	# Keep adding it to the block. When you get an if or while statement, you have to close this block, and update its 
	# goto. In the end just add an end block.
	block_list, bb_ctr, t_ctr, neg_ctr = body_statement_list(node, bb_ctr, t_ctr, neg_ctr)
	endblock = Block(bb_ctr, [], end=True)

	if len(node.operands) > 0 and node.operands[-1].operator == "RETURN" and len(node.operands[-1].operands) > 0:
		n, stmt_list, bb_ctr, t_ctr, neg_ctr = assignment_stmt_util(node.operands[-1].operands[0], bb_ctr, t_ctr, neg_ctr)
		stmt_list.append(AbstractSyntaxTreeNode("RETURN", [n]))
		endblock.addStmts(stmt_list)
	else:
		endblock.addStmts([AbstractSyntaxTreeNode("RETURN", [])])

	block_list.append(endblock)
	bb_ctr+=1

	# Here, we update the CFG to remove negative blocks
	# and append the actual values
	block_list = update_block_list(block_list) 

	return block_list, bb_ctr, t_ctr


def update_block_list(cfg):
	# This is the update function for the block list.
	# We go backwards and see the child of each backward statement.
	# g1 and g2 lists store the real goto of each block
	g1_list = []
	g2_list = []
	indexmap = {}
	for idx, blk in enumerate(cfg[:-1]):
		g1_list.append(blk.goto)
		g2_list.append(blk.goto2)
		indexmap[blk.number] = idx

	# Then, we go backwards to the blocks to update values using a Dynamic Programming approach
	for idx in range(len(cfg)-1)[::-1]:
		
		if cfg[idx].number < 0:
		# This is a dummy block, check if its goto is real, and if not, then update it to the real
		# value of the goto(next)
			if cfg[idx].goto < 0:
				next_block_idx = indexmap[cfg[idx].goto]
				g1_list[idx] = g1_list[next_block_idx]
			else:
				# The goto value points to a real block, so the mapping is already correct in g1_list
				pass
		else:
			# This is a real block, it may be a sequential block, or a conditional block
			if cfg[idx].goto2 is not None:
				# This is a conditional one
				if cfg[idx].goto2 < 0:
					next_block_idx = indexmap[cfg[idx].goto2]
					g2_list[idx]   = g1_list[next_block_idx]
					cfg[idx].goto2 = g1_list[next_block_idx]

			if cfg[idx].goto < 0:
				next_block_idx = indexmap[cfg[idx].goto]
				g1_list[idx]   = g1_list[next_block_idx]
				cfg[idx].goto  = g1_list[next_block_idx]

	new_cfg = []
	for b in cfg:
		if b.number > 0:
			new_cfg.append(b)

	return new_cfg


# util function for assignment statement
# Comes in handy to evaluate the list of statements corresponding to an expression
def assignment_stmt_util(node, bb_ctr, t_ctr, neg_ctr):
	# Assert that this is either a ptr_expr or a terminal
	# Input : A node which can contain any expr
	# Output: The first output is an RHS token (as an AST node)
	#		, the second one is the list of statements formed so far
	if node.operator in ["VAR", "CONST", "DEREF", "ADDR"]:
		return node, [], bb_ctr, t_ctr, neg_ctr
	elif node.operator == "FN_CALL":
		# Check out for params first
		stmt_list = []
		params = node.operands[0].operands
		n_fncall = deepcopy(node)
		n_fncall.operands[0].operands = []

		# Solve for every parameter
		for p in params:
			n, stm, bb_ctr, t_ctr, neg_ctr = assignment_stmt_util(p, bb_ctr, t_ctr, neg_ctr)
			stmt_list.extend(stm)
			n_fncall.operands[0].operands.append(n)
		return n_fncall, stmt_list, bb_ctr, t_ctr, neg_ctr

	else:
		if len(node.operands) == 2:
			# Check for left and right parts of the expression, solve them recursively
			n1, stmt1, bb_ctr, t_ctr, neg_ctr = assignment_stmt_util(node.operands[0], bb_ctr, t_ctr, neg_ctr)
			n2, stmt2, bb_ctr, t_ctr, neg_ctr = assignment_stmt_util(node.operands[1], bb_ctr, t_ctr, neg_ctr)
			n = AbstractSyntaxTreeNode(node.operator, [n1, n2])
			t0 = AbstractSyntaxTreeNode("VAR", [], "t" + str(t_ctr), tmp=True)
			t_ctr += 1
			asgn = AbstractSyntaxTreeNode("ASGN", [t0, n])
			stmt = stmt1 + stmt2 + [asgn]
			return t0, stmt, bb_ctr, t_ctr, neg_ctr
		elif len(node.operands) == 1:
			# UMINUS
			n1, stmt1, bb_ctr, t_ctr, neg_ctr = assignment_stmt_util(node.operands[0], bb_ctr, t_ctr, neg_ctr)
			n = AbstractSyntaxTreeNode(node.operator, [n1])
			t0 = AbstractSyntaxTreeNode("VAR", [], "t" + str(t_ctr), tmp=True)
			t_ctr += 1
			asgn = AbstractSyntaxTreeNode("ASGN", [t0, n])
			stmt = stmt1 + [asgn]
			return t0, stmt, bb_ctr, t_ctr, neg_ctr
		else:
			raise Exception


# This is for assignment statement list. If the next statement is an assignment, call the 
# assignment_statement_list on the node.
def assignment_statement_list(node, bb_ctr, t_ctr, neg_ctr):

	# This can either be an assignment or a function call. Check first.
	if node.operator == "ASGN":
		lhs = node.operands[0]
		rhs, stmt_list, bb_ctr, t_ctr, neg_ctr = assignment_stmt_util(node.operands[1], bb_ctr, t_ctr, neg_ctr)
		stmt_list.append(AbstractSyntaxTreeNode("ASGN", [lhs, rhs]))
		return stmt_list, bb_ctr, t_ctr, neg_ctr
	elif node.operator == "FN_CALL":
		N, stmt_list, bb_ctr, t_ctr, neg_ctr = assignment_stmt_util(node, bb_ctr, t_ctr, neg_ctr)
		stmt_list.append(N)
		return stmt_list, bb_ctr, t_ctr, neg_ctr



def condition_stmt_list(node, bb_ctr, t_ctr, neg_ctr):

	def condition_stmt_list_util(node, bb_ctr, t_ctr, neg_ctr):
		if node.operator in ["VAR", "CONST", "DEREF", "ADDR"]:
			return node, [], bb_ctr, t_ctr, neg_ctr
		else:
			if len(node.operands) == 2:
				n1, stmt1, bb_ctr, t_ctr, neg_ctr = condition_stmt_list_util(node.operands[0], bb_ctr, t_ctr, neg_ctr)
				n2, stmt2, bb_ctr, t_ctr, neg_ctr = condition_stmt_list_util(node.operands[1], bb_ctr, t_ctr, neg_ctr)
				n = AbstractSyntaxTreeNode(node.operator, [n1, n2])
				t0 = AbstractSyntaxTreeNode("VAR", [], "t" + str(t_ctr), tmp=True)
				t_ctr += 1
				asgn = AbstractSyntaxTreeNode("ASGN", [t0, n])
				stmt = stmt1 + stmt2 + [asgn]
				return t0, stmt, bb_ctr, t_ctr, neg_ctr
			elif len(node.operands) == 1:
				# This is the case of NOT
				n1, stmt1, bb_ctr, t_ctr, neg_ctr = condition_stmt_list_util(node.operands[0], bb_ctr, t_ctr, neg_ctr)
				n = AbstractSyntaxTreeNode(node.operator, [n1])
				t0 = AbstractSyntaxTreeNode("VAR", [], "t" + str(t_ctr), tmp=True)
				t_ctr += 1
				asgn = AbstractSyntaxTreeNode("ASGN", [t0, n])
				stmt = stmt1 + [asgn]
				return t0, stmt, bb_ctr, t_ctr, neg_ctr
			else:
				raise Exception

	# print(node.operator, len(node.operands))
	t1, stmt, bb_ctr, t_ctr, neg_ctr = condition_stmt_list_util(node, bb_ctr, t_ctr, neg_ctr)
	return stmt, bb_ctr, t_ctr, neg_ctr



def if_stmt_statement_list(node, bb_ctr, t_ctr, neg_ctr):
	# Assuming that the node is of an if-type
	# First, we check the condition, then recursively call the other two functions as and when necessary
	if_blk_list = []
	# Condition block first
	condition = node.operands[0]
	cond_block = Block(bb_ctr, [])
	bb_ctr += 1

	C, bb_ctr, t_ctr, neg_ctr = condition_stmt_list(condition, bb_ctr, t_ctr, neg_ctr)
	cond_block.addStmts(C)
	# Add an if statement here for the cond block
	# TODO
	# A generic function that returns a list of blocks for the body 
	# of the function. 
	# if_body has to contain at least one block, even if its nothing, so that we can specify a goto
	if_body, bb_ctr, t_ctr, neg_ctr = body_statement_list(node.operands[1], bb_ctr, t_ctr, neg_ctr)
	
	# If there is an empty body, we add a dummy body with a negative index on it
	if len(if_body) == 0:
		if_body = [Block(neg_ctr)]
		neg_ctr -= 1
	cond_block.goto = if_body[0].number

	# If there is an else part
	# if there is no else part, or empty else, we add a dummy else with negative index
	if len(node.operands) == 3:
		else_body, bb_ctr, t_ctr, neg_ctr = body_statement_list(node.operands[2], bb_ctr, t_ctr, neg_ctr)
		if len(else_body) == 0:
			else_body = [Block(neg_ctr)]
			neg_ctr -= 1
	else:
		else_body = [Block(neg_ctr)]
		neg_ctr -= 1
	cond_block.goto2 = else_body[0].number

	# Both the if body and else body point to this
	last_block = Block(neg_ctr)
	neg_ctr -= 1
	if_body[-1].goto = last_block.number
	else_body[-1].goto = last_block.number

	if_blk_list.append(cond_block)
	if_blk_list.extend(if_body)
	if_blk_list.extend(else_body)
	if_blk_list.append(last_block)
	return if_blk_list, bb_ctr, t_ctr, neg_ctr


def while_stmt_statement_list(node, bb_ctr, t_ctr, neg_ctr):
	while_blk_list = []

	condition = node.operands[0]
	cond_block = Block(bb_ctr, [])
	bb_ctr += 1

	C, bb_ctr, t_ctr, neg_ctr = condition_stmt_list(condition, bb_ctr, t_ctr, neg_ctr)
	cond_block.addStmts(C)

	while_body, bb_ctr, t_ctr, neg_ctr = body_statement_list(node.operands[1], bb_ctr, t_ctr, neg_ctr)
	
	# Check if the while body is empty
	if len(while_body) == 0:
		while_body = [Block(neg_ctr)]
		neg_ctr -= 1
	cond_block.goto = while_body[0].number
	while_body[-1].goto = cond_block.number

	last_block = Block(neg_ctr)
	neg_ctr -= 1
	cond_block.goto2 = last_block.number

	while_blk_list.append(cond_block)
	while_blk_list.extend(while_body)
	while_blk_list.append(last_block)
	return while_blk_list, bb_ctr, t_ctr, neg_ctr


# This is the caller function for the body.
# The node will only be of type "body"
def body_statement_list(node, bb_ctr, t_ctr, neg_ctr):
	# If there is nothing in the body, return a single stmt containing nothing. Will be useful for goto
	# of the condition as well as the outside of the if-block
	blk_body_list = []
	c_blk  = Block(bb_ctr, [])
	for op in node.operands:
		if op.operator == "ASGN":
			# If the statement is an assignment, simply add the statements to the current block
			C, bb_ctr, t_ctr, neg_ctr = assignment_statement_list(op, bb_ctr, t_ctr, neg_ctr)
			c_blk.addStmts(C)
		elif op.operator == "IF":
			# Check if there is a non-trivial block, if yes, then append it.
			# Then perform the if statement
			if c_blk.contents != []:
				bb_ctr += 1
				c_blk.goto = bb_ctr
				blk_body_list.append(c_blk)

			# Solve for the if-block and add it to the list
			if_blocks, bb_ctr, t_ctr, neg_ctr = if_stmt_statement_list(op, bb_ctr, t_ctr, neg_ctr)
			if len(blk_body_list) > 0:
				blk_body_list[-1].goto = if_blocks[0].number
			if_blocks[-1].goto = bb_ctr

			# We got a list of blocks
			c_blk = Block(bb_ctr, [])
			for blk in if_blocks:
				blk_body_list.append(blk)
		elif op.operator == "WHILE":
			# Check if there is a non-trivial block, if yes, then append it.
			# Then perform the 'while' statement
			if c_blk.contents != []:
				bb_ctr += 1
				c_blk.goto = bb_ctr
				blk_body_list.append(c_blk)

			while_blocks, bb_ctr, t_ctr, neg_ctr = while_stmt_statement_list(op, bb_ctr, t_ctr, neg_ctr)
			if len(blk_body_list) > 0:
				blk_body_list[-1].goto = while_blocks[0].number
			while_blocks[-1].goto = bb_ctr
			c_blk = Block(bb_ctr, [])
			for blk in while_blocks:
				blk_body_list.append(blk)

		elif op.operator == "FN_CALL":
			C, bb_ctr, t_ctr, neg_ctr = assignment_statement_list(op, bb_ctr, t_ctr, neg_ctr)
			c_blk.addStmts(C)

	if c_blk.contents != []:
		bb_ctr += 1
		c_blk.goto = bb_ctr
		blk_body_list.append(c_blk)


	return blk_body_list, bb_ctr, t_ctr, neg_ctr


#######################################################################################
## Some more functions to print AST in assignment-friendly form
#######################################################################################

def getParamsHeader(params):
	'''
	getParamsHeader gives a human-readable parameters list.
	params : params     - AST for params of function declaration
	returns: paramsStmt - string containing the params
	'''
	paramsStmt = ""
	for p in params.operands:
		vartype = p.vartype.name
		lvl, name = resolveParamName(p) 
		paramsStmt += "{0} {1}{2}, ".format(p.vartype.name, "*"*lvl, name)
	paramsStmt = paramsStmt[:-2]
	return paramsStmt


def getParamPrintable(vartype, lvl, name=""):
	'''
	Returns a string representation of a variable name, type, and level of indirection
	E.g. calling (int, 2, foo) return "int **foo" and calling (int, 3) returns "int***"
	'''
	derefs = lvl * "*"
	if name == "":
		return "{type}{derefs}".format(type=vartype, derefs=derefs)
	else:
		return "{type} {derefs}{name}".format(type=vartype, derefs=derefs, name=name)

def getProcedureTuple(name, symbolTable):
	''' Takes a function name and its symbol table, returns a tuple representing the procedure
	E.g. calling (func1, { ... }) returns ("func1", "int*", "int *x, int *y")
	'''
	params = symbolTable['params']
	paramsSorted = sorted(params.items(), key=lambda x: x[1]['pos'])
	paramsString = ", ".join([getParamPrintable(typeData['type'], typeData['lvl'], name) for name,typeData in paramsSorted])
	return (name, getParamPrintable(symbolTable['type'], symbolTable['lvl']), paramsString)

def resolveParamName(p):
	'''
	resolveParamName resolves the `ptr_expr_base` into level of indirection, and name
	params  : address or variable
	returns : lvl  - level of indirection
			  name - name of var
	'''
	if p.operator == "VAR":
		return 0, p.name
	elif p.operator == "DEREF":
		lvl, name = resolveParamName(p.operands[0])
		return lvl+1, name
	else:
		assert False
		return None, None

def proceduresInSymTable(globalTable):
	'''
	Takes a global symbol table and returns its nested procedures, return types, and parameter list
	returns: Array of tuples containing the function name, its return type, and parameter list as strings sorted by the function name
	'''
	procedures = { funcName:symbolTable for funcName,symbolTable in globalTable.items() if funcName != "main" and isinstance(symbolTable, dict) and symbolTable.get('func', False) }
	return [getProcedureTuple(name, symbolTable) for name, symbolTable in procedures.items()]

def variablesInSymbolTable(symbolTable, scope):
	''' Returns all the variables in a symbol table as tuples (name, scope, type, lvl) '''
	return [(name, scope, typeData['type'], typeData['lvl'] * "*") for name, typeData in symbolTable.items() if isinstance(typeData, dict) and typeData.get('func', False) == False]

def variablesOfGlobalTable(globalTable):
	''' Returns an array of all the variables declared in a global symbol table (including variables declared in functions)
	The result is returned as an array of tuples [(name, scope, base, derived type), ...]
	'''
	procedures = { funcName:symbolTable for funcName,symbolTable in globalTable.items() if isinstance(symbolTable, dict) and symbolTable.get('func', False) and symbolTable.get('proto', True)==False}
	variables = variablesInSymbolTable(globalTable, "global")
	for name, symbolTable in procedures.items():
		variables.extend(variablesInSymbolTable(symbolTable['decls'], "procedure {}".format(name)))
		variables.extend(variablesInSymbolTable(symbolTable['params'], "procedure {}".format(name)))
	return variables

def getASTPrintable(prog):
	'''
	Takes the AST data structure for the AST of the prog, and returns a string containing the 
	ASTs of the functions. 

	params:   prog - The AST for the entire program.
	returns:  stmt - The string containing the AST in printable form. To be dumped directly to the .ast file.
	'''
	decls, procedures = prog.operands
	stmt = ""
	
	# All functions
	for func in procedures.operands:
		part = ""
		# Get everything related to the func
		fname = func.name.name
		lvl   = func.name.lvl
		vartype = func.vartype.name
		params, _, body = func.operands

		part += "FUNCTION {0}\nPARAMS ({1})\nRETURNS {2}{3}\n".format(fname, getParamsHeader(params), "*"*lvl, vartype)
		# body is an AST node
		if len(body.operands) > 0:
			if body.operands[-1].operator == "RETURN":
				ret_stmt = body.operands[-1]
				l_stmts  = deepcopy(body)
				l_stmts.operands = l_stmts.operands[:-1]

				part+=l_stmts.__repr__(depth=1) 
				part+="\n"
				part+=ret_stmt.__repr__()
				part+="\n\n"
			else:
				part+=body.__repr__(depth=1)
				part+="\n\n"

			stmt+=part

	return stmt[:-2]

def getSYMPrintable(globalTable):
	''' Returns a string representation of the symbol table
		params: The global symbol table with the local symbol tables as children
	'''
	# Format procedure strings
	procedureTuples = proceduresInSymTable(globalTable)
	procedureStrings = ["{0}	|	{1}		|	{2}" \
		.format(*procedureTuple) for procedureTuple in procedureTuples]
	procedures = "\n".join(procedureStrings)

	# Format declaration strings
	variableTuples = variablesOfGlobalTable(globalTable)
	nameWidth = max(map(lambda x: len(x[0]), variableTuples)) + 2
	scopeWidth = max(map(lambda x: len(x[1]), variableTuples)) + 2
	typeWidth = len("Base Type") + 2
	variableStrings = ["{name: <{nameWidth}}|	{scope: <{scopeWidth}}|	{vartype: <{typeWidth}}|	{lvl}" \
		.format(name=name, scope=scope, vartype=vartype, lvl=lvl, nameWidth=nameWidth, scopeWidth=scopeWidth, typeWidth=typeWidth) for name, scope, vartype, lvl in variableTuples]
	variables = "\n".join(variableStrings)
	output = """
Procedure table :-
-----------------------------------------------------------------
Name	|	Return Type	|	Parameter List
{procedures}
-----------------------------------------------------------------
Variable table :- 
-----------------------------------------------------------------
{name: <{nameWidth}}|	{scope: <{scopeWidth}}|	{type: <{typeWidth}}|  Derived Type
-----------------------------------------------------------------
{variables}
-----------------------------------------------------------------
-----------------------------------------------------------------
""".format(procedures=procedures, variables=variables, name="Name", nameWidth=nameWidth, scope="Scope", scopeWidth=scopeWidth, type="Base Type", typeWidth=typeWidth)
	return output # Cleandoc cleans up indentation