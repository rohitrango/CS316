import os, sys
from utils import *

# TODO : Check for function main in the global Table later

def generateSymbolTable(declarations):
	'''
	Generates a symbols table from a list of declarations (AST Node).
	The symbol table is in the form of a dict object. 
	params : declarations - AST of declarations
	
	returns: symbolTable  - A dictionary of ID names and their attributes.
							For a var, the attrs are `type`, `lvl`, `func`: False
							For a func, the attrs are `type`, `lvl`, `name`, `func`: True, `proto`: True, `params`: dict{...}
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

			# Check if the function type is void with non-zero level of indirection
			if vartype.name == "void" and lvl != 0:
				messages.append("Function {0} cannot have return type as pointer to void. Error at line no. {1}".format(name, stmt.lineno))

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

def resolveDeclVar(v, allowAddr = False):
	'''
	Given a variable of type DEREF or INT, resolve the level of indirection 
	For the variable and return the name, lvl, and a list of errors that may have occured
	params : v 		    - a AST node which can be `DEREF`, `ID`, or `ADDR`
			 allowAddr  - Allow addresses in expressions? Useful for checking type of function, or LHS in an assignment.

	returns: name - name of the variable
			 lvl  - level of indirection of the variable
			 err  - Boolean saying if its an error or not
	'''
	# Returns the level of indirection of the variable
	op = v.operator
	if op == "VAR":
		return v.name, 0, False
	elif op == "DEREF":
		name, lvl, err = resolveDeclVar(v.operands[0])
		return name, lvl+1, err
	else:
		# In declarations and LHS of assignments, allowAddr is false and any found ADDR nodes will return as an error
		# In expressions, allowAddr is set to True and having ADDR nodes is fine
		# The grammar ensures that only one ADDR is in place
		name, lvl, err = resolveDeclVar(v.operands[0])
		err = not allowAddr
		return name, lvl - 1, err

def resolveType(name, symbolTable):
	'''
	Returns the type and the level of indirection for a variable in a symbol table
	Returns None, None, error messages as an array of strings if the variable is not specified

	Assertions: Assume that name is the name of a variable, otherwise check `typeCheckFunctionCall`.

	params: name 		- The `name` of the variable or function
			symbolTable - A symbolTable from where to search the name.
	
	returns: type - The type of the variable (could be 'int', 'float', or 'void')
			 lvl  - level of indirection as defined in the symbol table
			 err  - list of error messages
	'''

	# Search in the local symbol table
	for form in ['params', 'decls']:
		if form in symbolTable and name in symbolTable[form]:
			return symbolTable[form][name]['type'], symbolTable[form][name]['lvl'], []
		
	# Search in the global table
	if symbolTable['__parent__'] is not None and name in symbolTable['__parent__']:
		entry = symbolTable['__parent__'][name]
		if entry['func']:
			# Can only happen in the global symbol table because functions cannot
			# be declared inside other functions
			return None, None, ["Cannot use function `{0}` in an expression".format(name)]
		else:
			return entry['type'], entry['lvl'], []
	else:
		# TODO: Line number???
		return None, None, ["Variable {0} not defined".format(name)]

def generateParamsTable(params, decls):
	'''
	This takes a params object, and a symbol table, and returns a new symbol table with the parameters
	entered with some error messages that may have occured.

	params : params - A AST node containing a list of parameters
			 decls  - dictionary of declarations to be checked with the parameters.

	returns: paramsdict : A dictionary containing parameters and their types. The attributes are as follows: 
							- type : type of the variable,
							- lvl  : level of indirection as in the resolution from the declaration
							- pos  : position in the params
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
	
	Performs type checking along with the creation of the local symbol tables

	params:  proceduresAst - The list of procedures right after the declarations in the global scope
			 globalTable   - The global table passed

	returns: symbolTableList - List of local symbol tables
			 globalTable     - Modified global table
			 messages   	 - List of messages
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
		
		# Check if the function type is void with non-zero level of indirection
		if func.vartype.name == "void" and func.name.lvl != 0:
			messages.append("Function {0} cannot have return type as pointer to void. Error at line no. {1}".format(name, lineno))

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

				# Here, check for consistency of type and level of indirection
				if globalTable[name]['type'] != localSymbolTable['type']:
					messages.append("Function {0} has inconsistent type in definition and prototypes. Error at line no. {1}".format(name, lineno))
				if globalTable[name]['lvl'] != localSymbolTable['lvl']:
					messages.append("Function {0} has inconsistent level of indirection in definition and prototypes. Error at line no. {1}".format(name, lineno))

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


		# At this point, add the local Symbol table entry to the global symbol table
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

	params : body 				- an AST of type body. Contains a list of statements
			 localSymbolTable 	- The local symbol table of the procedure

	returns: errorMessages - List of error messages.

	'''
	errorMessages = []
	stmts = body.operands
	for stmt in stmts:
		# Check for what type of statement it is.
		op = stmt.operator
		if op == "ASGN":
			 errorMessages.extend(typeCheckExpr(stmt, localSymbolTable)[2])
		elif op == "IF" or op == "WHILE":
			errorMessages.extend(typeCheckExpr(stmt.operands[0], localSymbolTable)[2])
			for ifbody in stmt.operands[1:]:
				errorMessages.extend(typeCheckBody(ifbody, localSymbolTable))
		elif op == "FN_CALL":
			errorMessages.extend(typeCheckFunctionCall(stmt, localSymbolTable)[2])
		elif op == "RETURN":
			errorMessages.extend(typeCheckReturn(stmt, localSymbolTable))
		else:
			assert(False)

	return errorMessages

def typeCheckExpr(expr, symbolTable):
	'''
	Returns the type, the level of indirection, and list of all semantic errors in this expression for the given symbol table
	
	params:  expr - 	The expression to evaluate. This could be a simple VAR, ADDR, or something like PLUS, LT, etc.
			    		If the expression is a function call, then use the typeCheckFunctionCall() function.
			 symbolTable - The local symbol table of the procedure in which the expression is present.

	returns: type 			- The resulting type of the expression. Can be `int` or `float`. If the expression is invalid, return None.
			 lvl 			- The level of indirection of the resulting expression. If the expression is invalid, return None.
			 errorMessages  - The list of error messages.

	'''
	errorMessages = []
	if len(expr.operands) == 0 or len(expr.operands) == 1:
		operand = expr
		if operand.operator in ["VAR", "DEREF", "ADDR"]:
			# For variable, expr, deref, simply resolve the operand.
			name, derefLvl, err = resolveDeclVar(operand, True)
			vartype, declLvl, resolveTypeErrors = resolveType(name, symbolTable)
			errorMessages.extend(resolveTypeErrors)

			if vartype is None:
				return None, None, errorMessages

			# Check effective level and check if lvl >= 0
			lvl = declLvl - derefLvl
			if lvl < 0:
				errorMessages.append("Too much indirection in variable {0}. Error on lineno. {1}" \
					.format(name, expr.lineno))
				return None, None, errorMessages
			return vartype, lvl, errorMessages
		elif operand.operator == "CONST":
			# Separately for constant
			return operand.vartype, 0, errorMessages
		elif operand.operator == "FN_CALL":
			# For function call
			return typeCheckFunctionCall(operand, symbolTable)
		else:
			# Unary operator case
			return typeCheckExpr(operand.operands[0], symbolTable)
	else:
		assert(len(expr.operands) == 2)
		if expr.operator == "ASGN":
			# Check the LHS
			lhsName, lhsDerefLvl, err = resolveDeclVar(expr.operands[0])
			if err:
				errorMessages.append("LHS cannot contain &. Error on lineno. {0}".format(expr.lineno))
				return None, None, errorMessages

			lhsVartype, lhsDeclLvl, lhsResolveTypeErrors = resolveType(lhsName, symbolTable)
			errorMessages.extend(lhsResolveTypeErrors)

			if lhsVartype is None:
				return None, None, errorMessages

			lhsLvl = lhsDeclLvl - lhsDerefLvl
			if lhsLvl < 0:
				errorMessages.append("Too much indirection in variable {0}. Error on lineno. {1}" \
					.format(lhsName, expr.lineno))
				return None, None, errorMessages
		else:
			# Check the LHS
			lhsVartype, lhsLvl, lhsErrorMessages = typeCheckExpr(expr.operands[0], symbolTable)
			errorMessages.extend(lhsErrorMessages)
			if lhsVartype is None:
				return None, None, errorMessages

		# Check the RHS
		rhsVartype, rhsLvl, rhsErrorMessages = typeCheckExpr(expr.operands[1], symbolTable)
		errorMessages.extend(rhsErrorMessages)
		if rhsVartype is None:
			return None, None, errorMessages

		if lhsVartype != rhsVartype or lhsLvl != rhsLvl:
			errorMessages.append("Inconsistent types of operands. Error on line no. {0}" \
				.format(expr.lineno))
			return None, None, errorMessages

		return lhsVartype, lhsLvl, errorMessages

	# WARNING: You shouldn't hit this point, you are missing out on something.
	assert(False)
	return None, None, errorMessages

def typeCheckFunctionCall(stmt, symbolTable):
	'''
	Checks that a function with the given name and parameters exists in a symbol table
	Returns a list of errors messages as strings (empty if no errors were found)

	params:  stmt 			- Function call AST node  
			 symbolTable 	- local symbol table 

	returns: type 			- return type of the function call. Check from the symbol table.
			 lvl  			- level of indirection of the returned variable. Check from symbol table.
			 errorMessages 	- list of error messages
	'''
	errorMessages = []
	name = stmt.name

	# Check that the name exists in the global symbol table
	if name not in symbolTable['__parent__']:
		# !!! Line no. is not printed correctly
		errorMessages.append("Function {0} is not defined. Error on line no. {1}".format(name, stmt.lineno))
		return None, None, errorMessages

	# Check that the correct parameters have been provided
	# TODO: Change the parameters to expressions later
	# Change the providedParams, and then do the checks accordingly
	functionSymbolTable = symbolTable['__parent__'][name]
	
	providedParams = list(resolveDeclVar(x) for x in stmt.operands[0].operands)
	requiredParams = list(sorted(functionSymbolTable['params'].values(), key=lambda x: x['pos']))

	# Arguments count
	if len(providedParams) != len(requiredParams):
		errorMessages.append("Wrong number of arguments provided for function {0}. {1} provided, should be {2}. Error on line no. {3}" \
			.format(name, len(providedParams), len(requiredParams), stmt.lineno))
		return None, None, errorMessages
	
	# For each provided parameter, check that its type matches the type defined in the function declaration
	for idx, ((providedName, providedLvl, _), required) in enumerate(zip(providedParams, requiredParams)):
		varType, varLvl, resolveTypeErrors = resolveType(providedName, symbolTable)
		if varType is None:
			# The variable did not exist in the symbol table
			errorMessages.extend(resolveTypeErrors)
			return None, None, errorMessages

		if varType != required['type']:
			errorMessages.append("Wrong type for parameter {0} in function call {1}. Received {2}, expected {3}. Error on line no. {4}" \
				.format(str(idx), name, varType, required['type'], stmt.lineno))
			return None, None, errorMessages

		calledLvl = varLvl - providedLvl
		if calledLvl != required['lvl']:
			errorMessages.append("Wrong level of indirection for parameter {0} in function call {1}. Error on line no. {2}" \
				.format(str(idx), name, stmt.lineno))
			return None, None, errorMessages

	# Check for too much indirection
	lvl = functionSymbolTable['lvl'] - stmt.lvl
	if lvl < 0:
		errorMessages.append("Too much indirection for function call {0}. Error on line no. {1}".format(name, stmt.lineno))
		return None, None, errorMessages

	return functionSymbolTable['type'], lvl, errorMessages

def typeCheckReturn(return_stmt, symbolTable):
	'''
	Gets a return statement and checks if it matches with the type and level of indirection of the expression.

	params:  return_stmt - The AST node of type RETURN and optionally containing a return value.
			 symbolTable - Symbol table of the local function

	returns: errorMessages - List of error messages
	'''
	errorMessages = []
	assert(return_stmt.operator == "RETURN")
	op = return_stmt.operands
	if len(op) == 0:
		# No parameters
		lvl = 0
		vartype = "void"
	elif len(op) == 1:
		# One parameter, check if its a void function
		vartype, lvl, errorMessages = typeCheckExpr(op[0], symbolTable)
		if symbolTable['type'] == "void":
			errorMessages.append("void function `{0}` can't return anything in line no. {1}".format(symbolTable['name'], return_stmt.lineno))
			return errorMessages
	else:
		print("ASSERTION ERROR: Check typeCheckReturn")
		assert(False)

	# Check for the type of function
	if vartype != symbolTable['type'] and vartype is not None:
		errorMessages.append("Incorrect return type in function `{0}` at line no. {1}".format(symbolTable['name'], return_stmt.lineno))

	if lvl != symbolTable['lvl'] and lvl is not None:
		errorMessages.append("Incorrect type of indirection in function `{0}` in line no. {1}".format(symbolTable['name'], return_stmt.lineno))

	return errorMessages
