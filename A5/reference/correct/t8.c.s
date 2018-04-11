
	.data


	.text	# The .text assembler directive indicates
	.globl main	# The following is the code
main:

# Prologue begins
	sw $ra, 0($sp)	# Save the return address
	sw $fp, -4($sp)	# Save the frame pointer
	sub $fp, $sp, 8	# Update the frame pointer

	sub $sp, $sp, 20	# Make space for the locals
# Prologue ends

label0:
	addi $v0, $sp, 8
	sw $v0, 0($sp)
	li $v0, 5
	lw $t0, 0($sp)
	sw $v0, 0($t0)
	j label1
label1:
t0
	lw $v0, 0($sp)
	lw $t1, 0($v0)
	li $v0, 4
	slt $t2, $v0, $t1
	move $v0, $t2
	not $t1, $v0
	move $v0, $t1
	bne $v0, $0, label2
	j label3
label2:
	li $t1, 4
	lw $t2, 4($sp)
	sw $t1, 0($t2)
	j label1
label3:
	j epilogue_main


# Epilogue begins
epilogue_main:
	add $sp, $sp, 20
	lw $fp, -4($sp)
	lw $ra, 0($sp)
	jr $31	# Jump back to the called procedure
# Epilogue ends

