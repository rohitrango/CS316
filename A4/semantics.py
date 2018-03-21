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
		if stmt.operator == "DECL":

			# This is for a declaration statement
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
		else:
			# This is for function prototype
			# stmt is of type "F_PROTO", operands contains the parameters, name contains fname
			vartype = stmt.operands[0]
			params = stmt.operands[1]
			paramsTable, messages = generateParamsTable(params, dict())
			name = stmt.name.name
			lvl  = stmt.name.lvl

			# Check if the definition is in the symbol table already, if not, then add it 
			if name in symbol_table:
				messages.append("Declaration of {0} is done more than once. Error at line no. {1}".format(name, stmt.lineno))

			# Entry for function prototype
			symbol_table[name] = {
				'type': vartype.name,
				'lvl': lvl, 
				'scope': 'local', 
				'func': True, 
				'proto': True,
				'params': paramsTable	
			}


	return symbol_table, messages

def resolveDeclVar(v):
	'''
	Given a variable of type DEREF or INT, resolve the level of indirection 
	For the variable and return the name, lvl, and a list of errors that may have occured
	'''
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
	'''
	This takes a params object, and a symbol table, and returns a new symbol table with the parameters
	entered with some error messages that may have occured.
	'''
	messages = []
	for idx, param in enumerate(params.operands):
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

		symbolTable[name] = { "type": param.vartype.name , "lvl": lvl, 'scope': 'param', 'pos': idx}
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

		# Use name and lineno for errors.
		lineno = func.name.lineno
		name = func.name.name

		localSymbolTable = dict()
		params, decls, body = func.operands
		localSymbolTable, declsMessages = generateSymbolTable(decls)
		localSymbolTable, localMessages = generateParamsTable(params, localSymbolTable)

		# Add the self reference to the local symbol table
		# So that we cannot define variables having the same name as the function inside.
		# Then, we add a self reference to make things easy when we check for the function name itself.
		if name in localSymbolTable:
			messages.append("Parameter or declaration cannot be function name {0}, error at line no. {1}".format(name, lineno))
		localSymbolTable[name] = {
			'type': func.vartype.name,
			'lvl': func.name.lvl,
			'scope': 'local', 
			'func': True, 
			'proto': False,
		}

		messages.extend(localMessages)
		messages.extend(declsMessages)

		# At this point, localSymbolTable contains all declarations and parameters
		localSymbolTable['__parent__'] = globalTable
		localSymbolTable['__name__'] = func.name.name
		localSymbolTable['__lvl__'] = func.name.lvl
		symbolTableList.append(localSymbolTable)

		# Check for the same name in the global table.
		# If the name is present and it's not a prototype, append a message accordingly.
		# If its a prototype, check for lvl and type of variables

		if name in globalTable:
			if not globalTable[name].get('proto', False):
				messages.append("Function {0} is already declared. Error at line no. {1}".format(name, lineno))
			else:
				# Prototype is defined, check for consistency of positions and types of parameters
				# Take dictionaries for both the prototype, and definition
				# Compare them, and add error messages accordingly
				protoParams = sorted(globalTable[name]['params'].values(), key=lambda x: x['pos'])
				defParams   = filter(lambda x: isinstance(x, dict) and x.get('scope', '') == "param", localSymbolTable.values())
				defParams   = sorted(defParams, key=lambda x: x['pos'])
				if len(defParams) == len(protoParams):
					for idx, (defParam, protoParam) in enumerate(zip(defParams, protoParams)):
						# Check for inconsistent types
						if (defParam['lvl'] != protoParam['lvl']) or (defParam['type'] != protoParam['type']):
							messages.append("Function {0} has inconsistent type of parameter, at param. index: {1}. Error at line no. {2}".format(name, idx, lineno))
				else:
					messages.append("Function {0} has inconsistent number of parameters. Error at line no. {1}".format(name, lineno))


		# Here, if all declarations are correct, do type checking for the function
		# if len(messages) == 0:
		# 	err_messages = typeCheckBody(body, localSymbolTable)
		# 	messages.extend(err_messages)

		# Add a reference to the function, since another function defined later
		# Should be able to refer to this function via the global table
		globalTable[name] = {
					'type': func.vartype.name,
					'lvl': func.name.lvl,
					'scope': 'local', 
					'func': True, 
					'proto': False
		}

	return symbolTableList, globalTable, messages


# Do type checking. Call some recursive functions depending upon the type of node
def typeCheckBody(body, localSymbolTable):
	'''
	Takes in a body (from function body, if or while statements)
	Uses local symbol table to check for types
	'''
	errorMessages = []
	stmts = body.operands
	for stmt in stmts:
		# Check for what type of statement it is.
		op = stmt.operator
		if op == "ASGN":
			 errorMessages.extend(typeCheckExpr(stmt.operands, localSymbolTable))
		elif op == "IF" or op == "WHILE":
			errorMessages.extend(typeCheckExpr(stmt.operands[0], localSymbolTable))
			for ifbody in stmt.operands[1:]:
				errorMessages.extend(typeCheckBody(ifbody, localSymbolTable))
		elif op == "FN_CALL":
			errorMessages.extend(typeCheckFunctionCall(stmt.name, stmt.operands[0], localSymbolTable))
		else:
			errorMessages.extend(typeCheckReturn(stmt.operands[0], localSymbolTable))

	return errorMessages

def typeCheckExpr(expr, symbolTable):
	return []

def typeCheckFunctionCall(name, params, symbolTable):
	return []

def typeCheckReturn(expr, symbolTable):
	return []
