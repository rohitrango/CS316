'''
-----------------------------------------------------------------------
Data Structure for Abstract Syntax Tree
-----------------------------------------------------------------------
'''

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

	def __init__(self, operator, operands=[], name=None):
		self.operator = operator
		self.name = name
		self.operands = operands

	def addChild(self, child):
		self.operands.append(child)

	def __repr__(self, depth=0):
		# print(self.operator, len(self.operands))
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

	# This function gives the CFG printable equivalent
	# Change this as you wish
	def printable(self):
		if self.operator == "ASGN":
			return self.operands[0].printable() + " = " + self.operands[1].printable()
		elif self.operator in ["VAR", "CONST"]:
			return self.name
		elif self.operator == "ADDR":
			return "&" + self.operands[0].printable()
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
		else:
			print(self)
			raise Exception


# This is for body statements since they are printed differently in the reference implementation
class AbstractBodyTreeNode(AbstractSyntaxTreeNode):
	def __init__(self, operator, operands=[], name=None):
		super(AbstractBodyTreeNode, self).__init__(operator, operands, name)

	def __repr__(self, depth=0):
		res = ""
		for child in self.operands:
			if child.operator!="DECL":
				res += child.__repr__(depth=depth)+"\n"
		return res


#########################################
## Block class
#########################################
class Block(object):

	def __init__(self, number, contents=[], goto=None, goto2=None):
		self.goto = goto
		self.goto2 = goto2
		self.number = number
		self.contents = contents

	def addStmts(self, stmts):
		# Assuming that stmts is a list
		if isinstance(stmts, list):
			self.contents.extend(stmts)
		else:
			# Shouldn't occur
			raise NotImplementedError

	def __repr__(self):
		string = "<bb" + str(self.number) + ">"
		for op in self.contents:
			string += ("\n" + op.printable())
		if self.goto2 is None:
			string += ("\ngoto <bb" + str(self.goto) + ">")
		else:
			string += ("\nif(" + self.contents[-1].printable().split(" ")[0] + ") goto <bb" + str(self.goto) + ">")
			string += ("\nelse goto <bb" + str(self.goto2) + ">")
		return string


# generate the CFG given a node
def generateCFG(node):
	bb_ctr = 1
	t_ctr  = 0

	# Master code. Keep a list of block iterms along with the current block. As you keep getting more statements,
	# Keep adding it to the block. When you get an if or while statement, you have to close this block, and update its 
	# goto. In the end just add an end block.
	block_list = []
	cur_block  = Block(bb_ctr, [])
	for op in node.operands:
		if op.operator == "ASGN":
			# This is an assignment, here, we put in the assignment
			# add all the statements as a part of the block.
			# C contains all the assignments that were formed as part of the single complex
			# assignment statement. cur_block simply takes in all the statements
			C, bb_ctr, t_ctr = assignment_statement_list(op, bb_ctr, t_ctr)
			cur_block.addStmts(C)
		elif op.operator == "IF":
			# Here, C will return a list of blocks, instead of a list of statements.
			# The job is to check all the blocks which do not have a goto, and assign a goto as the one
			if cur_block.contents != []:
				bb_ctr += 1
				block_list.append(cur_block)

			if_blocks, bb_ctr, t_ctr = if_stmt_statement_list(op, bb_ctr, t_ctr)
			if len(block_list) > 0:
				block_list[-1].goto = if_blocks[0].number
			bb_ctr += 1
			if_blocks[-1].goto = bb_ctr
			# We got a list of blocks
			cur_block = Block(bb_ctr, [])
			for blk in if_blocks:
				block_list.append(blk)
		elif op.operator == "WHILE":

			if cur_block.contents != []:
				bb_ctr += 1
				cur_block.goto = bb_ctr
				block_list.append(cur_block)

			while_blocks, bb_ctr, t_ctr = while_stmt_statement_list(op, bb_ctr, t_ctr)
			if len(block_list) > 0:
				block_list[-1].goto = while_blocks[0].number
			while_blocks[-1].goto = bb_ctr
			cur_block = Block(bb_ctr, [])
			for blk in while_blocks:
				block_list.append(blk)

	if len(cur_block.contents) > 0:
		block_list.append(cur_block)

	return block_list

# This is for assignment statement list. If the next statement is an assignment, call the 
# assignment_statement_list on the node.
def assignment_statement_list(node, bb_ctr, t_ctr):

	def assignment_stmt_util(node, bb_ctr, t_ctr):
		# Assert that this is either a ptr_expr or a terminal
		# Input : A node which can contain any expr
		# Output: The first output is an RHS token (as an AST node)
		#		, the second one is the list of statements formed so far
		if node.operator in ["VAR", "CONST", "DEREF", "ADDR"]:
			return node, [], bb_ctr, t_ctr
		else:
			if len(node.operands) == 2:
				# Check for left and right parts of the expression, solve them recursively
				n1, stmt1, bb_ctr, t_ctr = assignment_stmt_util(node.operands[0], bb_ctr, t_ctr)
				n2, stmt2, bb_ctr, t_ctr = assignment_stmt_util(node.operands[1], bb_ctr, t_ctr)
				n = AbstractSyntaxTreeNode(node.operator, [n1, n2])
				t0 = AbstractSyntaxTreeNode("VAR", [], "t" + str(t_ctr))
				t_ctr += 1
				asgn = AbstractSyntaxTreeNode("ASGN", [t0, n])
				stmt = stmt1 + stmt2 + [asgn]
				return t0, stmt, bb_ctr, t_ctr
			elif len(node.operands) == 1:
				# UMINUS
				n1, stmt1, bb_ctr, t_ctr = assignment_stmt_util(node.operands[0], bb_ctr, t_ctr)
				n = AbstractSyntaxTreeNode(node.operator, [n1])
				t0 = AbstractSyntaxTreeNode("VAR", [], "t" + str(t_ctr))
				t_ctr += 1
				asgn = AbstractSyntaxTreeNode("ASGN", [t0, n])
				stmt = stmt1 + [asgn]
				return t0, stmt, bb_ctr, t_ctr
			else:
				raise Exception

	# Assert that this is an assignment node
	lhs = node.operands[0]
	rhs, stmt_list, bb_ctr, t_ctr = assignment_stmt_util(node.operands[1], bb_ctr, t_ctr)
	stmt_list.append(AbstractSyntaxTreeNode("ASGN", [lhs, rhs]))
	return stmt_list, bb_ctr, t_ctr


def condition_stmt_list(node, bb_ctr, t_ctr):

	def condition_stmt_list_util(node, bb_ctr, t_ctr):
		if node.operator in ["VAR", "CONST", "DEREF", "ADDR"]:
			return node, [], bb_ctr, t_ctr
		else:
			if len(node.operands) == 2:
				n1, stmt1, bb_ctr, t_ctr = condition_stmt_list_util(node.operands[0], bb_ctr, t_ctr)
				n2, stmt2, bb_ctr, t_ctr = condition_stmt_list_util(node.operands[1], bb_ctr, t_ctr)
				n = AbstractSyntaxTreeNode(node.operator, [n1, n2])
				t0 = AbstractSyntaxTreeNode("VAR", [], "t" + str(t_ctr))
				t_ctr += 1
				asgn = AbstractSyntaxTreeNode("ASGN", [t0, n])
				stmt = stmt1 + stmt2 + [asgn]
				return t0, stmt, bb_ctr, t_ctr
			elif len(node.operands) == 1:
				# This is the case of NOT
				n1, stmt1, bb_ctr, t_ctr = condition_stmt_list_util(node.operands[0], bb_ctr, t_ctr)
				n = AbstractSyntaxTreeNode(node.operator, [n1])
				t0 = AbstractSyntaxTreeNode("VAR", [], "t" + str(t_ctr))
				t_ctr += 1
				asgn = AbstractSyntaxTreeNode("ASGN", [t0, n])
				stmt = stmt1 + [asgn]
				return t0, stmt, bb_ctr, t_ctr
			else:
				raise Exception

	# The base case has to contain two operands
	# print(node.operator, len(node.operands))
	assert(len(node.operands) == 2)
	t1, stmt, bb_ctr, t_ctr = condition_stmt_list_util(node, bb_ctr, t_ctr)
	# t0 = AbstractSyntaxTreeNode("VAR", [], "t" + str(t_ctr))
	# t_ctr += 1
	# asgn = AbstractSyntaxTreeNode("ASGN", [t0, t1])
	# stmt = stmt + [asgn]
	return stmt, bb_ctr, t_ctr



def if_stmt_statement_list(node, bb_ctr, t_ctr):
	# Assuming that the node is of an if-type
	# First, we check the condition, then recursively call the other two functions as and when necessary
	if_blk_list = []
	# Condition block first
	condition = node.operands[0]
	cond_block = Block(bb_ctr, [])
	bb_ctr += 1

	C, bb_ctr, t_ctr = condition_stmt_list(condition, bb_ctr, t_ctr)
	cond_block.addStmts(C)
	# Add an if statement here for the cond block
	# TODO
	# A generic function that returns a list of blocks for the body 
	# of the function. 
	# if_body has to contain at least one block, even if its nothing, so that we can specify a goto
	if_body, bb_ctr, t_ctr = body_statement_list(node.operands[1], bb_ctr, t_ctr)
	if len(if_body) == 0:
		if_body = [Block(bb_ctr)]
		bb_ctr += 1
	cond_block.goto = if_body[0].number

	if len(node.operands) == 3:
		else_body, bb_ctr, t_ctr = body_statement_list(node.operands[2], bb_ctr, t_ctr)
		if len(else_body) == 0:
			else_body = [Block(bb_ctr)]
			bb_ctr += 1
	else:
		else_body = [Block(bb_ctr)]
		bb_ctr += 1
	cond_block.goto2 = else_body[0].number

	# Both the if body and else body point to this
	last_block = Block(bb_ctr)
	bb_ctr += 1
	if_body[-1].goto = last_block.number
	else_body[-1].goto = last_block.number

	if_blk_list.append(cond_block)
	if_blk_list.extend(if_body)
	if_blk_list.extend(else_body)
	if_blk_list.append(last_block)
	return if_blk_list, bb_ctr, t_ctr


def while_stmt_statement_list(node, bb_ctr, t_ctr):
	while_blk_list = []

	condition = node.operands[0]
	cond_block = Block(bb_ctr, [])
	bb_ctr += 1

	C, bb_ctr, t_ctr = condition_stmt_list(condition, bb_ctr, t_ctr)
	cond_block.addStmts(C)

	while_body, bb_ctr, t_ctr = body_statement_list(node.operands[1], bb_ctr, t_ctr)
	if len(while_body) == 0:
		while_body = [Block(bb_ctr)]
		bb_ctr += 1
	cond_block.goto = while_body[0].number
	while_body[-1].goto = cond_block.number

	last_block = Block(bb_ctr)
	bb_ctr += 1
	cond_block.goto2 = last_block.number

	while_blk_list.append(cond_block)
	while_blk_list.extend(while_body)
	while_blk_list.append(last_block)
	return while_blk_list, bb_ctr, t_ctr


# This is the caller function for the body.
# The node will only be of type "body"
def body_statement_list(node, bb_ctr, t_ctr):
	# If there is nothing in the body, return a single stmt containing nothing. Will be useful for goto
	# of the condition as well as the outside of the if-block
	blk_body_list = []
	c_blk  = Block(bb_ctr, [])
	for op in node.operands:
		if op.operator == "ASGN":
			C, bb_ctr, t_ctr = assignment_statement_list(op, bb_ctr, t_ctr)
			c_blk.addStmts(C)
		elif op.operator == "IF":
			if c_blk.contents != []:
				bb_ctr += 1
				c_blk.goto = bb_ctr
				blk_body_list.append(c_blk)

			if_blocks, bb_ctr, t_ctr = if_stmt_statement_list(op, bb_ctr, t_ctr)
			if len(blk_body_list) > 0:
				blk_body_list[-1].goto = if_blocks[0].number
			if_blocks[-1].goto = bb_ctr
			# We got a list of blocks
			c_blk = Block(bb_ctr, [])
			for blk in if_blocks:
				blk_body_list.append(blk)
		elif op.operator == "WHILE":
			if c_blk.contents != []:
				bb_ctr += 1
				c_blk.goto = bb_ctr
				blk_body_list.append(c_blk)

			while_blocks, bb_ctr, t_ctr = while_stmt_statement_list(op, bb_ctr, t_ctr)
			if len(blk_body_list) > 0:
				blk_body_list[-1].goto = while_blocks[0].number
			while_blocks[-1].goto = bb_ctr
			c_blk = Block(bb_ctr, [])
			for blk in while_blocks:
				blk_body_list.append(blk)
	if c_blk.contents != []:
		bb_ctr += 1
		blk_body_list.append(c_blk)
	return blk_body_list, bb_ctr, t_ctr