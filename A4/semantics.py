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
				symbol_table[name] = {'type': vartype.name, 'lvl': lvl, 'func': False}
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
				'name': name,
				'type': vartype.name,
				'lvl': lvl, 
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

def resolveType(name, symbolTable):
	'''
	Returns the type and the level of indirection for a variable in a symbol table
	Returns None, None if the variable is not specified
	'''
	for form in ['params', 'decls']:
		if form in symbolTable and name in symbolTable[form]:
			return symbolTable[form][name]['type'], symbolTable[form][name]['lvl']
		
	# if name in symbolTable:
	# 	return symbolTable[name]['type'], symbolTable[name]['lvl']
	if symbolTable['__parent__'] is not None and name in symbolTable['__parent__']:
		entry = symbolTable['__parent__'][name]
		return entry['type'], entry['lvl']
	else:
		return None, None

def generateParamsTable(params, decls):
	'''
	This takes a params object, and a symbol table, and returns a new symbol table with the parameters
	entered with some error messages that may have occured.
	'''
	paramsdict = dict()
	messages = []
	for idx, param in enumerate(params.operands):
		name, lvl, err = resolveDeclVar(param)
		if err:
			messages.append("Declaration of {0} cannot contain symbol '&' at line no. {1}".format(name, param.lineno))
		
		if param.vartype.name == "void":
			messages.append("Declaration of parameter {0} cannot be void, at line no. {1}".format(name, param.lineno))

		# Check for the name in either parameters or declarations
		if name in paramsdict:
			messages.append("Parameter of name {0} is used more than once. Error at line no. {1}".format(name, param.lineno))
		elif name in decls:
			messages.append("Declaration of name {0} is used as a parameter. Error at line no. {1}".format(name, param.lineno))

		paramsdict[name] = { "type": param.vartype.name , "lvl": lvl, 'pos': idx}
	return paramsdict, messages

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

		# Generate params and declarations
		params, decls, body = func.operands
		# First, generate the symbol table for the function
		# Then, we generate the parameters table for the function
		# Check if any parameter is defined as a declaration before
		declsTable, declsMessages = generateSymbolTable(decls)
		paramsTable, localMessages = generateParamsTable(params, declsTable)

		# Add the self reference to the local symbol table
		# So that we cannot define variables having the same name as the function inside.
		# Then, we add a self reference to make things easy when we check for the function name itself.
		if name in paramsTable or name in declsTable:
			messages.append("Parameter or declaration cannot be function name {0}, error at line no. {1}".format(name, lineno))
		
		# This is the local symbol table. Contains the following:
		#  	- It's own name
		# 	- type
		# 	- level of indirection
		# 	- func: If it's a function or not. 
		#	- Proto: If it's a proto or not.
		#	- params: Dictionary of parameters 
		# 	- decls : Dictionary of declarations
		localSymbolTable = {
			'name': name,
			'type': func.vartype.name,
			'lvl': func.name.lvl,
			'func': True, 
			'proto': False,
			'params': paramsTable,
			'decls' : declsTable,
			'__parent__': globalTable,
		}


		messages.extend(localMessages)
		messages.extend(declsMessages)

		# At this point, localSymbolTable contains all declarations and parameters
		symbolTableList.append(localSymbolTable)

		# Check for the same name in the global table.
		# If the name is present and it's not a prototype, append a message accordingly.
		# If its a prototype, check for lvl and type of variables
		if name in globalTable:
			if not globalTable[name].get('proto', False):
				messages.append("Function {0} is already declared / named as variable. Error at line no. {1}".format(name, lineno))
			else:
				# Prototype is defined, check for consistency of positions and types of parameters
				# Take dictionaries for both the prototype, and definition
				# Compare them, and add error messages accordingly
				protoParams = sorted(globalTable[name]['params'].values(), key=lambda x: x['pos'])
				defParams   = sorted(localSymbolTable['params'].values(), key=lambda x: x['pos'])

				if len(defParams) == len(protoParams):
					for idx, (defParam, protoParam) in enumerate(zip(defParams, protoParams)):
						# Check for inconsistent types
						if (defParam['lvl'] != protoParam['lvl']) or (defParam['type'] != protoParam['type']):
							messages.append("Function {0} has inconsistent type of parameter, at param. index: {1}. Error at line no. {2}".format(name, idx, lineno))
				else:
					messages.append("Function {0} has inconsistent number of parameters. Error at line no. {1}".format(name, lineno))

		# Add a reference to the function, since another function defined later
		# should be able to refer to this function via the global table
		# !!! Should this really be done? We're discarding parameter information above
		globalTable[name] = localSymbolTable
		
		# Here, if all declarations are correct, do type checking for the function
		if len(messages) == 0:
			bodyErrorMesages = typeCheckBody(body, localSymbolTable)
			messages.extend(bodyErrorMesages)

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
			errorMessages.extend(typeCheckFunctionCall(stmt, localSymbolTable))
		else:
			errorMessages.extend(typeCheckReturn(stmt.operands[0], localSymbolTable))

	return errorMessages

def typeCheckExpr(expr, symbolTable):
	return []

def typeCheckFunctionCall(stmt, symbolTable):
	'''
	Checks that a function with the given name and parameters exists in a symbol table
	Returns a list of errors messages as strings (empty if no errors were found)
	'''
	errorMessages = []
	name = stmt.name

	# Check that the name exists in the global symbol table
	if name not in symbolTable['__parent__']:
		# !!! Line no. is not printed correctly
		print(name, symbolTable['__parent__'])
		errorMessages.append("Function {0} is not defined. Error on line no. {1}".format(name, stmt.lineno))
		return errorMessages

	# Check that the correct parameters have been provided
	# TODO: Change the parameters to expressions later
	# Change the providedParams, and then do the checks accordingly
	providedParams = list(resolveDeclVar(x) for x in stmt.operands[0].operands)
	requiredParams = list(sorted(symbolTable['params'].values(), key=lambda x: x['pos']))
	if len(providedParams) != len(requiredParams):
		errorMessages.append("Wrong number of arguments provided for function {0}. {1} provided, should be {2}. Error on line no. {3}" \
			.format(name, len(providedParams), len(requiredParams), stmt.lineno))
		return errorMessages
	
	# For each provided parameter, check that its type matches the type defined in the function declaration
	for idx, ((providedName, providedLvl, _), required) in enumerate(zip(providedParams, requiredParams)):
		varType, varLvl = resolveType(providedName, symbolTable)
		if varType != required['type']:
			errorMessages.append("Wrong type for parameter {0} in function call {1}. Received {2}, expected {3}. Error on line no. {4}" \
				.format(str(idx), name, varType, required['type'], stmt.lineno))
		calledLvl = varLvl - providedLvl
		if calledLvl != required['lvl']:
			errorMessages.append("Wrong level of indiretion for parameter {0} in function call {1}. Error on line no. {2}" \
				.format(str(idx), name, stmt.lineno))

	return errorMessages

def typeCheckReturn(expr, symbolTable):
	return []
