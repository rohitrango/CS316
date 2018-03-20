import os, sys
from utils import *

# TODO : Check for function main in the global Table later

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
			symbol_table[name] = {'type': vartype.name, 'lvl': lvl, 'scope': 'decl'}

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

def generateParamsTable(params, symbolTable):
	messages = []
	for param in params.operands:
		name, lvl, err = resolveDeclVar(param)
		if err:
			messages.append("Declaration of {0} cannot contain symbol '&' at line no. {1}".format(name, param.lineno))
		
		if param.vartype.name == "void":
			messages.append("Declaration of parameter {0} cannot be void, at line no. {1}".format(name, param.lineno))

		if name in symbolTable:
			if symbolTable[name]['scope'] == 'param':
				messages.append("Parameter of name {0} is used more than once. Error at line no. {1}".format(name, param.lineno))
			else:
				messages.append("Declaration of name {0} is used as a parameter. Error at line no. {1}".format(name, param.lineno))

		symbolTable[name] = { "type": param.vartype.name , "lvl": lvl, 'scope': 'param' }
	return symbolTable, messages

def generateLocalTables(proceduresAst, globalTable):
	'''
	Takes in a list of procedures, and the global table to generate a list of local tables, for each function
	And also check the type for the statements
	'''
	procedures = proceduresAst.operands
	symbolTableList = []
	messages = []

	# Do this for all procedures
	for func in procedures:
		localSymbolTable = dict()
		params, decls, body = func.operands
		localSymbolTable, declsMessages = generateSymbolTable(decls)
		localSymbolTable, localMessages = generateParamsTable(params, localSymbolTable)

		messages.extend(localMessages)
		messages.extend(declsMessages)
		# Check that the variables declared in the procedure don't occur as parameters
		# for name, content in declsSymbolTable.items():
		# 	if name in paramsSymbolTable: # TODO: Introduce line number
		# 		messages.append("Redefinition of {0}, already used as parameter. Error at line no. {1}".format(name, ))
		localSymbolTable['__parent__'] = globalTable
		localSymbolTable['__name__'] = func.name
		symbolTableList.append(localSymbolTable)

		# Check for the same name in the global table, else add it to the global symbol table
		name = func.name
		if name in globalTable:
			messages.append("Function {0} is already declared. Error at line no. {1}".format(name, func.lineno))

		globalTable[name] = {'type': func.vartype.name, 'lvl': 0, 'scope': 'local', 'func': True}

	return symbolTableList, globalTable, messages

