import os, sys
from utils import *

def generateSymbolTable(declarations):
	'''
	Generates a symbols table from a list of declarations (AST Node).
	The symbol table is in the form of a dict object. 
	'''
	messages = []
	symbol_table = dict()

	decl_stmts = declarations.operands
	for stmt in decl_stmts:
		vartype, decl_list = stmt.operands
		# Check for void type declarations here
		if vartype.name == "void":
			messages.append("Declaration cannot be of type : {0} at line no. {1}".format(vartype.name, vartype.lineno))
		
		# Resolve all variables
		for var in decl_list.operands:
			name, lvl, err = resolveDeclVar(var)
			if err:
				messages.append("Declaration of {0} cannot contain symbol '&' at line no. {1}".format(name, vartype.lineno))
			if name in symbol_table:
				messages.append("Declaration of {0} is done more than once. Error at line no. {1}".format(name, vartype.lineno))
			
			# Update the level of indirection of the variable in the symbol table
			# TODO : Change it to a more complex form as and when needed.
			symbol_table[name] = {'type': vartype.name, 'lvl': lvl}

	return symbol_table, messages

def resolveDeclVar(v):
	# Returns the level of indirection of the variable
	op = v.operator
	if op == "VAR":
		return v.name, 0, False
	elif op == "DEREF":
		name, lvl, err = resolveDeclVar(v.operands[0])
		return name, lvl+1, err
	else:
		# This is the error case
		name, lvl, err = resolveDeclVar(v.operands[0])
		err = True
		return name, lvl, err

