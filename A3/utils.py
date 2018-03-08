'''
-----------------------------------------------------------------------
Data Structure for Abstract Syntax Tree
-----------------------------------------------------------------------
'''

sym_to_name_mapping = {
	'PLUS'	: '+',
	'MINUS'	: '-',
	'DIV' 	: '/',
	'MUL'	: '(',
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
			return self.operands[0].printable() + " " + sym_to_name_mapping[self.operator] + " " + self.operands[1].printable()



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

	def __init__(self, number, contents):
		self.number = number
		self.contents = contents

class Statement(object):
	def __init__(self, op, params):
		self.op = op
		self.params = params


# generate the CFG given a node
def generateCFG(node):
	bb_ctr = 0
	t_ctr  = 0

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
					n1, stmt1, bb_ctr, t_ctr = assignment_stmt_util(node.operands[0], bb_ctr, t_ctr)
					n2, stmt2, bb_ctr, t_ctr = assignment_stmt_util(node.operands[1], bb_ctr, t_ctr)
					n = AbstractSyntaxTreeNode(node.operator, [n1, n2])
					t0 = AbstractSyntaxTreeNode("VAR", [], "t" + str(t_ctr))
					t_ctr += 1
					asgn = AbstractSyntaxTreeNode("ASGN", [t0, n])
					stmt = stmt1 + stmt2 + [asgn]
					return t0, stmt, bb_ctr, t_ctr
				else:
					return node.operands[0], [], bb_ctr, t_ctr


		# Assert that this is an assignment node
		lhs = node.operands[0]
		rhs, stmt_list, bb_ctr, t_ctr = assignment_stmt_util(node.operands[1], bb_ctr, t_ctr)
		stmt_list.append(AbstractSyntaxTreeNode("ASGN", [lhs, rhs]))
		return stmt_list, bb_ctr, t_ctr

	def if_stmt_statement_list(node, bb_ctr, t_ctr):
		return None, bb_ctr, t_ctr

	def while_stmt_statement_list(node, bb_ctr, t_ctr):
		return None, bb_ctr, t_ctr

	block_list = []
	for op in node.operands:
		if op.operator == "ASGN":
			C, bb_ctr, t_ctr = assignment_statement_list(op, bb_ctr, t_ctr)
		elif op.operator == "IF":
			C, bb_ctr, t_ctr = if_stmt_statement_list(op, bb_ctr, t_ctr)
		else:
			C, bb_ctr, t_ctr = while_stmt_statement_list(op, bb_ctr, t_ctr)
		if C:
			block_list = block_list + C
	return block_list
