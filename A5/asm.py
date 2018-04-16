from utils import variablesInSymbolTable

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
    out.extend(["# Prologue begins", "\tsw $ra, 0($sp)  # Save the return address", "\tsw $fp, -4($sp) # Save the frame pointer", "\tsub $fp, $sp, 8 # Update the frame pointer"])

    decls = globalTable[name]['decls']
    varToStackMap = dict()
    offset = 0
    for idx, varname in enumerate(sorted(decls.keys())):
        vartype = decls[varname]['type']
        lvl = decls[varname]['lvl']
        offset += 4 if lvl != 0 or vartype == 'int' else 8
        varToStackMap[varname] = {
            'offset': offset,
            'type': vartype,
            'lvl': lvl,
            'stackPos': idx,
        }
    out.append("\tsub $sp, $sp, {0}    # Make space for the locals".format(offset+8))
    out.append("# Prologue ends")
    return out, varToStackMap, offset


def functionBodyAsAsm(globalTable, blocks, name, varToStackMap):
    return []


def epilougeAsAsm(name, offset):
    """
    Given the name of function, and the offset, output its epilouge
    """
    out = ["# Epilogue begins",
                "epilogue_{0}:".format(name),
                "\tadd $sp, $sp, {0}".format(8+offset),
                "\tlw $fp, -4($sp)",
                "\tlw $ra, 0($sp)",
                "\tjr $ra  # Jump back to the called procedure",
                "# Epilogue ends",
        ]
    return out