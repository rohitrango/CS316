
	.data


	.text	# The .text assembler directive indicates
	.globl main	# The following is the code
main:

# Prologue begins
	sw $ra, 0($sp)	# Save the return address
	sw $fp, -4($sp)	# Save the frame pointer
	sub $fp, $sp, 8	# Update the frame pointer

	sub $sp, $sp, 12	# Make space for the locals
# Prologue ends

label0:
	li $t4, 5
	lw $t0, 0($sp)
	sw $t4, 0($t0)
	j label1
label1:
	j epilogue_main


# Epilogue begins
epilogue_main:
	add $sp, $sp, 12
	lw $fp, -4($sp)
	lw $ra, 0($sp)
	jr $31	# Jump back to the called procedure
# Epilogue ends

