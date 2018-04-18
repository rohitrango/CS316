from utils import variablesInSymbolTable
from heapq import heapify, heappush, heappop
# Methods for converting symbol tables and CFGs into assembly

def asAsm(globalTable, cfgs):
    '''
    Returns the MIPS assembly code for a global symbol table and an array of CFGs
    '''
    symbolTableAsm = symbolTableAsAsm(globalTable)
    # For each function, we have a list
    # supposed to contain .globl <func_name> for each function
    funcAsm = functionAsAsm(globalTable, cfgs)

    return "\n".join(["", *symbolTableAsm, "", *funcAsm])

def symbolTableAsAsm(globalTable):
    '''
    Returns the global symbol table as an array of strings representing a MIPS .data section
    '''
    out = ["    .data"]
    # Retrieve the global variables and sort them by name
    globalVariables = variablesInSymbolTable(globalTable, "global")
    globalVariables = sorted(globalVariables, key=lambda x: x[0])
    for name, _, vartype, _ in globalVariables:
        space = ".space	8" if vartype == "float" else ".word	0"
        out.append("global_{0}:	{1}".format(name, space))
    return out


def functionAsAsm(globalTable, cfgs):
    '''
    Takes a list of CFGs and returns a list of .s code
    Params: globalTable - global symbol table
            cfgs - list of cfgs
    '''
    out = []

    # Run for all functions
    for funcBlock in cfgs:
        name = funcBlock.name
        blocks = funcBlock.blocks

        # Use textAsm to compile all the required code
        textAsm = ["\t.text", "\t.global {0}".format(name), "{0}:".format(name)]
        prolouge, varToStackMap, offset = prologueAsAsm(globalTable, name)
        body = functionBodyAsAsm(globalTable, blocks, name, varToStackMap)
        epilouge = epilougeAsAsm(name, offset)

        out.extend(textAsm)
        out.extend(prolouge)
        out.extend(body)
        out.extend(epilouge)
    
    return out


def prologueAsAsm(globalTable, name):
    '''
    Given the name of the function, create an activation record
    '''
    out = []
    out.extend(["# Prologue begins", "\tsw $ra, 0($sp)\t# Save the return address", "\tsw $fp, -4($sp)\t# Save the frame pointer", "\tsub $fp, $sp, 8\t# Update the frame pointer"])

    decls = globalTable[name]['decls']

    # Params will be a list of 2-tuples, for key and values
    params = globalTable[name]['params']
    params = sorted(params.items(), key=lambda x: x[1]['pos'])

    varToStackMap = dict()
    offset = 0
    for idx, varname in enumerate(sorted(decls.keys())):
        vartype = decls[varname]['type']
        lvl = decls[varname]['lvl']
        # Take care of int and float pointers here
        offset += 4 if lvl != 0 or vartype == 'int' else 8
        varToStackMap[varname] = {
            'offset': offset,
            'type': vartype,
            'lvl': lvl,
            'stackPos': idx,
            'decl':True,
        }

    declsOffset = offset
    # In the interest of $ra and $fp
    offset += 8
    # Fill in the key value pairs now
    for varname, attr in params:
        vartype = attr['type']
        lvl     = attr['lvl']
        offset += 4 if lvl != 0 or vartype == 'int' else 8
        varToStackMap[varname] = {
            'offset': offset,
            'type'  : vartype,
            'lvl'   : lvl,
            'stackPos': attr['pos'],
            'decl'  : False,
        }

    # print(varToStackMap)
    out.append("\tsub $sp, $sp, {0}\t# Make space for the locals".format(declsOffset+8))
    out.append("# Prologue ends")
    return out, varToStackMap, declsOffset

#####
# Helper functions that return the assembly code for a given RHS
#####
def resolveOffset(name, globalTable, varToStackMap):
    '''
    Given the name of a variable and a globalTable, resolve the offset
    '''
    if name in varToStackMap:
        return "{0}($sp)".format(varToStackMap[name]['offset'])
    else:
        return "global_{0}".format(name)



def unaryAsAsm(node, globalTable, intRegisters, tmpToRegMap, varToStackMap, indent=False, lhsMode=False):
    '''
    Takes a node containing a unary operator, and returns list of assembly statements
    '''
    def indentStmts(out):
        # Indent only at the last level
        if indent:
            out = list(map(lambda x: "\t"+x, out))
        return out

    # Main loop
    out = []
    if node.operator == "CONST" and node.vartype == "int":
        freeReg = heappop(intRegisters)
        stmt = "li $s{0}, {1}".format(freeReg, node.name)
        out.append(stmt)
        return indentStmts(out), freeReg

    # For uminus, solve the expression recursively
    elif node.operator == "UMINUS":
        # Solve for the operand inside uminus
        node = node.operands[0]
        tmpout, tmpLatestReg = unaryAsAsm(node, globalTable, intRegisters, tmpToRegMap, varToStackMap)
        out.extend(tmpout)

        stmt = "sub $s{0}, $0, $s{0}".format(tmpLatestReg)
        out.append(stmt)
        return indentStmts(out), tmpLatestReg

    # Deal with int variables
    elif node.operator == "VAR" and node.vartype == "int":
        if node.tmp:
            return [], tmpToRegMap[node.name]
        else:
            # Do a symbol table check
            freeReg = heappop(intRegisters)
            stmt = "lw $s{0}, {1}".format(freeReg, resolveOffset(node.name, globalTable, varToStackMap))
            out.append(stmt)
            return indentStmts(out), freeReg

    # Deal with derefs
    elif node.operator == "DEREF" and node.vartype == "int":
        derefCount = 0

        while node.operator == "DEREF" or node.operator == "ADDR":
            derefCount += 1 if node.operator == "DEREF" else -1
            node = node.operands[0]
        # This node is now a VAR
        freeReg = heappop(intRegisters)
        out.append("lw $s{0}, {1}".format(freeReg, resolveOffset(node.name, globalTable, varToStackMap)))

        minDerefCount = 1 if lhsMode else 0

        while derefCount > minDerefCount:
            anotherFreeReg = heappop(intRegisters)
            out.append("lw $s{0}, 0($s{1})".format(anotherFreeReg, freeReg))
            heappush(intRegisters, freeReg)
            freeReg = anotherFreeReg
            derefCount-=1
        return indentStmts(out), freeReg

    # Deal with address
    elif node.operator == "ADDR":
        node = node.operands[0]
        freeReg = heappop(intRegisters)
        if node.name in varToStackMap:
            stmt = "addi $s{0}, $sp, {1}".format(freeReg, varToStackMap[node.name]['offset'])
        else:
            stmt = "la $s{0}, global_{1}".format(freeReg, node.name)
        out.append(stmt)
        return indentStmts(out), freeReg


    print(node.operator, node.name , node.vartype)
    return out, -1


operatorToAsm = {
    'PLUS': 'add',
    'MINUS': 'sub',
    'MUL': 'mul',
    'DIV': 'div',
}

def functionBodyAsAsm(globalTable, blocks, name, varToStackMap):
    out = []

    # Code for heap of free registers and dictionary for tmp variables
    intRegisters = list(range(8))
    heapify(intRegisters)
    tmpToRegMap  = dict()

    for block in blocks:
        # First the label number
        out.append("label{0}:".format(block.number-1))

        # Now loop thru the statements
        for stmt in block.contents:
            # Check for various cases here
            if stmt.operator == "ASGN":
                lhs, rhs = stmt.operands
                if len(rhs.operands) <= 1:
                    # Unary operator, can be NOT, UMINUS, VAR, DEREF, CONST
                    outputRHS, rhsReg = unaryAsAsm(rhs, globalTable, intRegisters, tmpToRegMap, varToStackMap, indent=True)
                    out.extend(outputRHS)

                    # Check type of LHS and allocate accordingly
                    if lhs.operator == "VAR" and lhs.tmp and lhs.vartype == "int":
                        tmpToRegMap[lhs.name] = rhsReg

                    # This could be a deref or var
                    elif lhs.operator == "VAR" and lhs.vartype == "int":
                        # Do a symbol table check
                        stmt = "\tsw $s{0}, {1}".format(rhsReg, resolveOffset(lhs.name, globalTable, varToStackMap))
                        # Free the RHS reg and add the statement
                        heappush(intRegisters, rhsReg)
                        out.append(stmt)

                    # If its a deref, just use unary
                    elif lhs.operator == "DEREF" and lhs.vartype == "int":
                        outputLHS, lhsReg = unaryAsAsm(lhs, globalTable, intRegisters, tmpToRegMap, varToStackMap, indent=True, lhsMode=True)
                        out.extend(outputLHS)
                        stmt = "\tsw $s{0}, 0($s{1})".format(rhsReg, lhsReg)
                        heappush(intRegisters, rhsReg)
                        heappush(intRegisters, lhsReg)
                        out.append(stmt)
                
                # This is the end of unary functions and their corresponding code generator
                # Now we solve for the second part, which deals with binary ops
                else:
                    # Resolve the two operands of the RHS
                    op1, op2 = rhs.operands
                    op1Asm, op1Reg = unaryAsAsm(op1, globalTable, intRegisters, tmpToRegMap, varToStackMap, indent=True)
                    op2Asm, op2Reg = unaryAsAsm(op2, globalTable, intRegisters, tmpToRegMap, varToStackMap, indent=True)
                    out.extend(op1Asm)
                    out.extend(op2Asm)

                    # Get a result registry
                    resReg = heappop(intRegisters)

                    # Append the operations, handle divs separately because it stores the result differently 
                    if rhs.operator == "DIV":
                        out.append("\t{0} $s{1}, $s{2}".format(operatorToAsm[rhs.operator], op1Reg, op2Reg))
                        out.append("\tmflo $s{0}".format(resReg))
                    else:
                        out.append("\t{0} $s{1}, $s{2}, $s{3}".format(operatorToAsm[rhs.operator], resReg, op1Reg, op2Reg))

                    # Free up the registers used for the operations
                    heappush(intRegisters, op1Reg)
                    heappush(intRegisters, op2Reg)

                    # Move the result into place and free the result registry (done by the reference implementation)
                    movReg = heappop(intRegisters)
                    out.append("\tmove $s{0}, $s{1}".format(movReg, resReg))
                    heappush(intRegisters, resReg)

                    # Store what registry the LHS temporary "variable" resides in 
                    tmpToRegMap[lhs.name] = movReg

        ### End of the block statements, check goto and assign statements here
        if block.end:
            # This is the return block. This just needs a return value and it will jump straight to the 
            # epilogue part
            return_stmt = block.contents[-1]
            if len(return_stmt.operands) > 0:
                ret_value = return_stmt.operands[0]
                # Check for the type of return
                if ret_value.operator == "CONST" and ret_value.vartype == "int":
                    # return only an int constant
                    freeReg = heappop(intRegisters)
                    stmt = "\tli $s{0}, {1}".format(freeReg, ret_value.name)
                    stmt2 = "\tmove $v1, $s{0} # move return value to $v1".format(freeReg)
                    heappush(intRegisters, freeReg)
                    out.extend([stmt, stmt2])
                # Else, it could be a parameter
            out.append("\tj epilogue_{0}\n".format(name))
        
        # This is the other part, where it jumps to a next block or two
        else:
            if block.goto2 is None:
                out.append("\tj label{0}".format(block.goto-1))




    return out


def epilougeAsAsm(name, offset):
    """
    Given the name of function, and the offset, output its epilouge
    """
    out = ["# Epilogue begins",
                "epilogue_{0}:".format(name),
                "\tadd $sp, $sp, {0}".format(8+offset),
                "\tlw $fp, -4($sp)",
                "\tlw $ra, 0($sp)",
                "\tjr $ra\t# Jump back to the called procedure",
                "# Epilogue ends",
        ]
    return out