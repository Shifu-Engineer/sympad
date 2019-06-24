import re

FUNCS_PY = list (reversed (sorted ('''
	abs
	expand
	factor
	factorial
	simplify
	'''.replace (',', ' ').strip ().split ())))

FUNCS_PY_AND_TEX = list (reversed (sorted ('''
	arg
	ln
	'''.replace (',', ' ').strip ().split ())))

rec_num_int        = re.compile (r'^-?\d+$')
rec_num_pos_int    = re.compile (r'^\d+$')
rec_var_diff_start = re.compile (r'^d(?=[^_])')
rec_var_part_start = re.compile (r'^\\partial ')
rec_var_not_single = re.compile (r'^(?:d.|\\partial |.+_)')

def is_int_text (text): # >= 0
	return rec_num_pos_int.match (text)

def is_pos_num (ast): # >= 0
	return ast [0] == '#' and ast [1] [0] != '-'

def is_neg_num (ast): # < 0
	return ast [0] == '#' and ast [1] [0] == '-'

def is_pos_int (ast): # >= 0
	return ast [0] == '#' and rec_num_pos_int.match (ast [1])

def is_neg (ast):
	return \
			ast [0] == '-' or \
			ast [0] == '#' and ast [1] [0] == '-' or \
			ast [0] == '*' and is_neg (ast [1])

def is_differential_var (ast):
	return ast [0] == '@' and rec_var_diff_start.match (ast [1])

def is_partial_var (ast):
	return ast [0] == '@' and rec_var_part_start.match (ast [1])

def is_single_unit (ast): # is single positive digit or single non-differential non-subscripted variable?
	if ast [0] == '#':
		return len (ast [1]) == 1

	return ast [0] == '@' and not rec_var_not_single.match (ast [1])

def strip_paren (ast):
	return ast [1] if ast [0] == '(' else ast

def flatcat (op, ast0, ast1): # ,,,/O.o\,,,~~
	if ast0 [0] == op:
		if ast1 [0] == op:
			return ast0 + ast1 [1:]
		return ast0 + (ast1,)
	elif ast1 [0] == op:
		return (op, ast0) + ast1 [1:]
	return (op, ast0, ast1)
