#!/usr/bin/env python

from getopt import getopt
from random import random, randrange, choice
import sys

import sast
from sast import AST
import sym
import sparser

TERMS = [
	'0',
	'1',
	'-1',
	'1.0',
	'-1.0',
	# '1e-100',
	# '1e100',
	# '1e+100',
	'a',
	"a'",
	'd',
	'dx',
	'partial',
	'partialx',
	'oo',
	"'str'",
]

_EXPRESSIONS = r"""
\sqrt[{{1} / {1.0}}]{({oo},{partial})}
sqrt{{-1.0}**{0}}
{{\frac{1.0}{dx}} \cdot {{partial} / {partialx}} \cdot {{d} >= {oo}}}
\frac{{partial}**{1}}{{{partialx}*{dx}*{1.0}}}
{{\frac{1.0}{partialx}} \cdot {\exp({0},{a})} \cdot {{{d}+{oo}}}}
{\arcsin({-1.0},{dx},{oo})}^{{d} <= {-1}}
@({{d}**{1}},{\arcsech({partial},{partial})})
Limit ({d} > {-1.0}, x, {{1.0}*{partial}*{dx}})
{{d}^{1}} / {{{dx}  {oo}}}
{{{d}*{1}}} / {partial^{5} / partialy^{1} partialy^{2} partialz^{2} {oo}}
{{{0}!} \cdot {partial^{1} / partialx^{1} {dx}} \cdot {{d}**{d}}}
{{partial^{4} / partialy^{3} partialy^{1} {a}} \cdot {{'str'}^{d}}}
{\int {-1} dx} / {\int {1} dx}
{\int_{dx}^{a'} {-1} dx}!
\int {partial^{3} / partialy^{3} {a'}} dx
{{\int {partial} dx}  {partial^{4} / partialy^{1} partialz^{1} partialz^{2} {a}}}
\int_{[{-1.0}]}^{\int {partialx} dx} {{{oo}+{-1}}} dx
\int_{partial^{6} / partialy^{2} partialx^{2} partialz^{2} {partialx}}^{partial^{4} / partialz^{1} partialz^{2} partialx^{1} {0}} {{a} != {'str'}} dx
{{{oo}**{'str'}}+{\int {oo} dx}+{partial^{7} / partialz^{3} partialx^{2} partialx^{2} {0}}}
[{{{-1} \cdot {oo}}},{{{dx},{1.0},{oo}}},{partial^{8} / partialx^{3} partialx^{2} partialz^{3} {oo}}]
-{lambda x, y, z: {dx}}
('-', ('lamb', ('@', 'dx'), (('@', 'x'), ('@', 'y'), ('@', 'z'))))
{{lambda x, y, z: {1}}+{{1.0} > {1.0}}+{{oo} / {'str'}}}
{{lambda: {-1}} \cdot {\frac{partialx}{oo}} \cdot {{1.0} if {1} else {a'} if {0}}}
{{{a'} / {-1}} {\lim_{x \to partial} {-1}} {lambda x, y, z: {partialx}}}
{{{{d}*{0}}}+{{'str'}**{d}}+{lambda x, y: {partialx}}}
\int_{\sqrt[{a}]{1.0}}^{[]} {lambda x: {partialx}} dx
lambda x: {{dx} = {dx}}
{{\lim_{x \to {{oo},}} {\frac{d}{d}}}  {{{{{partialx} \cdot {a'}}} \cdot {{{a'}*{'str'}}}}}}
\int {{{{a} / {dx}}  {partial^{2} / partialz^{2} {partialx}}}} dx
\int \frac{d}{dx} x dx
\int d / dx x dx
\int_{{partial^{4} / partialx^{1} partialy^{3} {partial}}**{\sqrt[{oo}]{0}}}^{{{{-1} == {0}}*{({partial},{'str'},{a'})}*{{1} / {1}}}} {-{partial^{6} / partialy^{3} partialx^{3} {0}}} dx
\int {-{partial^{6} / partialy^{3} partialx^{3} {0}}} dx
\lim_{x \to \frac{lambda x, y, z: {-{0}}}{partial^{5} / partialz^{2} partialz^{1} partialx^{2} {Limit (a', x, 1)}}} {\arctan()}
{{{|{{0}**{1.0}}|} / {lambda x, y: {\int_{a'}^{a'} {0} dx}}},{\int_{\sqrt{()}}^{lambda x, y, z: {Sum (partial, (x, a, partial))}} {lambda x, y: {{{1}*{a'}}}} dx},}
-{{{{{{partialx},{partial},{oo},},{{dx},{-1.0},{a},},}}**{StrictGreaterThan({1.0})}} > {partial^{4} / partialz^{1} partialx^{2} partialy^{1} {{1.0}^{1}}}}
-{{{{{\sum_{x = 0}^{-1.0} {oo}} \cdot {({0})}}},}}
\int {{{{d}+{partialx}+{1}}} if {lambda x, y, z: {a}} else {{1} / {partialx}}} dx
|{\log_{partial^{1} / partialy^{1} {{{0}*{'str'}}}}{[{{-1.0} / {'str'}}]}}|
|{Limit ({\frac{1}{-1.0}}!, x, ({{{{-1.0},},{{1},},}},{{{'str'} \cdot {1} \cdot {dx}}},{-{1}}))}|
('|', ('lim', ('!', ('/', ('#', '1'), ('#', '-1.0'))), ('@', 'x'), ('(', (',', (('vec', (('#', '-1.0'), ('#', '1'))), ('*', (('"', 'str'), ('#', '1'), ('@', 'dx'))), ('-', ('#', '1'))))), '+'))
{\lim_{x \to -1.0} {dx}} > {{oo} if {-1.0} else {d} if {d} else {1}}
\frac{{-1.0} > {oo}}{\ln{-1.0}}
{{{{{{0},},}},{|{d}|},},{{({1.0},{1})},{[{oo}]},},}
1/2 * {a+b} lambda: {d}
{{{'str'} < {1.0}} \cdot {({a'})} \cdot {{1} if {a'}}}
-{1.0 if partial else d if 1 else oo if 1.0 else 'str'}
{partial^{5} / partialy^{2} partialy^{2} partialy^{1} {partial}}^{{-1.0} > {d}}
{lambda x: {a}} if {{{'str'}*{a}*{1}}}
\int_{{-1.0} <= {1}}^{-{1}} {{-1.0} <= {1.0}} dx
{{({{{a'},},{{1.0},},})}+{{a}!}+{{d} if {1} else {dx}}}
\int_{{{a}+{a}+{0}}}^{{'str'} / {a}} {\int {1} dx} dx
lambda x: {lambda x, y: {oo}}
\sqrt[3]{({oo},{a'})}
Limit (\sum_{x = oo}^{partial} {-1.0}, x, \sec({-1.0},{-1},{partialx}))
{{a} = {partial}} if {{{oo}+{0}+{-1}}} else {\int {a} dx}
\sum_{x = {{1}*{d}*{oo}}}^{\exp({a'},{1})} {\log_{1.0}{a}}
lambda x: {{a} = {dx}}
{{{d}^{oo}}*{{a}^{d}}}
{{oo} if {oo}} = {is_mersenne_prime({'str'})}
\lim_{x \to 0} {sqrt(dx) lambda x, y: -1.0}
{{\frac{\int_{a}^{1} {dx} dx}{{{oo} \cdot {d} \cdot {dx}}}}}
\frac{{{lambda x, y: {({{1},{partial},})}}*{lambda: {-{1}}}}}{\sum_{x = {({{d},})} / {{partialx} if {0} else {dx} if {partialx} else {d} if {partial}}}^{{{{1} = {partial}}  {\sum_{x = partial}^{-1} {oo}}}} {-{{{'str'}  {1}}}}}
\int d/dx dx
(((-1)**partial)**({a_prime, oo, 'str'}))**-{-{0}}
Limit ({{{0}^{'str'}}  {\left|{a}\right|}  {({a},{a'})}}, x, lambda x: {{1}!})
\left(\left(\text{'str'} \right)! \le \left(\left(x, y \right) \mapsto -1.0 \right) \right) == \int_{\left[-1.0, \partial, -1 \right]}^{\log_{-1.0}\left(-1 \right)} \begin{cases} 1 & \text{for}\: \infty \\ 1.0 & \text{for}\: 1.0 \end{cases} \ dx
x^{-{{1} / {1.0}}}
cofactors( 1 , {lambda x: 1 = lambda: 2} )
({{{-{cse()}},{{{{partial} != {-1}}*{{{-1.0}  {1.0}}}}},{lambda: {{-1.0} == {dx}}},},{{\lim_{x \to \log_{0}{d}} {[{-1.0}]}},{partial^{7} / partialx^{3} partialy^{1} partialx^{3} {{partialx} if {a'} else {-1.0} if {a} else {d} if {1.0} else {partialx}}},{{lambda x, y, z: {oo}} = {\tanh()}},},{{partial^{3} / partialz^{3} {{oo} / {'str'}}},{({{{\left|{dx}\right|},{{a} if {d}},},{{-{oo}},{({{-1.0},{oo},{-1.0},})},},})},{partial^{5} / partialx^{1} partialy^{1} partialz^{3} {{-1}!}},},})
{\left|{a}\right|} if {\int {'str'} dx} else {({-1},{-1},{a})} if {\left|{1.0}\right|}
{lambda x: {{1.0} if {oo} else {1.0} if {oo}}} = {{{{partial} \cdot {partialx}}}**{{a}!}}
{Sum (\int {1} dx, (x, 0, 1))} dx
{{\sum_{x = \left|{0}\right|}^{\tan({-1.0})} {\int_{partialx}^{oo} {d} dx}}+{{{\lim_{x \to 1} {d}} \cdot {{{a'}+{-1}+{dx}}}}}+{{{{a} = {a'}}+{({{{dx},},{{0},},{{d},},})}+{{{dx}*{dx}*{a'}}}}}}
log(partialx*'str'*partialx) / log(Derivative(a, z, 3, y, 2))
abs(e**sqrt1, abs(-1.0))
dpartial
""".strip ().split ('\n')

def expr_eq (): ## BROKEN!
	return f'{expr ()} {choice (["=", "==", "!=", "<", "<=", ">", ">="])} {expr ()}'

def expr_paren ():
	return '(' + ','.join (f'{expr ()}' for i in range (randrange (4))) + ')'

def expr_brack ():
	return '[' + ','.join (f'{expr ()}' for i in range (randrange (4))) + ']'

def expr_abs ():
	return f'\\left|{expr ()}\\right|'

def expr_minus ():
	return f'-{expr ()}'

def expr_fact ():
	return f'{expr ()}!'

def expr_add ():
	return '{' + '+'.join (f'{expr ()}' for i in range (randrange (2, 4))) + '}'

def expr_mul_imp ():
	return '{' + '  '.join (f'{expr ()}' for i in range (randrange (2, 4))) + '}'

def expr_mul_exp ():
	return '{' + '*'.join (f'{expr ()}' for i in range (randrange (2, 4))) + '}'

def expr_mul_cdot ():
	return '{' + ' \\cdot '.join (f'{expr ()}' for i in range (randrange (2, 4))) + '}'

def expr_div ():
	return f'{expr ()} / {expr ()}'

def expr_frac ():
	return f'\\frac{expr ()}{expr ()}'

def expr_caret ():
	return f'{expr ()}^{expr ()}'

def expr_dblstar ():
	return f'{expr ()}**{expr ()}'

def expr_log ():
	return \
			choice (['', '\\']) + f'{choice (["ln", "log"])}{expr ()}' \
			if random () >= 0.5 else \
			f'\\log_{expr ()}{expr ()}'

def expr_sqrt ():
	return \
			choice (['', '\\']) + f'sqrt{expr ()}' \
			if random () >= 0.5 else \
			f'\\sqrt[{expr ()}]{expr ()}'

def expr_func ():
	while 1:
		py = choice (list (AST.Func.PY))

		if py not in sparser._FUNC_AST_XLAT and py not in sym._ast2tex_func_xlat:
			break

	return \
			'\\' + f'{choice (list (AST.Func.TEX))}{expr_paren ()}' \
			if random () >= 0.5 else \
			f'{py}{expr_paren ()}' \

def expr_lim ():
	return \
			'\\lim_{x \\to ' + f'{expr ()}}} {expr ()}' \
			if random () >= 0.5 else \
			f'Limit ({expr ()}, x, {expr ()})'

def expr_sum ():
	return \
			'\\sum_{x = ' + f'{expr ()}}}^{expr ()} {expr ()}' \
			if random () >= 0.5 else \
			f'Sum ({expr ()}, (x, {expr ()}, {expr ()}))'

def expr_diff ():
	d  = 'd' # choice (['d', 'partial'])
	p  = 0
	dv = []

	for _ in range (randrange (1, 4)):
		n  = randrange (1, 4)
		p += n

		dv.append ((choice (['x', 'y', 'z']), n))

	return \
			f'{d}^{{{p}}} / {" ".join (f"{d + v}^{{{dp}}}" for v, dp in dv)} {expr ()}'
			# if random () >= 0.5 else \
			# f'Derivative ({expr ()}, {", ".join (f"{v}, {dp}" for v, dp in dv)})'

def expr_intg ():
	return \
			f'\\int_{expr ()}^{expr ()} {expr ()} dx' \
			if random () >= 0.5 else \
			f'\\int {expr ()} dx'

def expr_vec ():
	return '({' + ','.join (f'{expr ()}' for i in range (randrange (1, 4))) + ',})'

def expr_mat ():
	cols = randrange (1, 4)

	return '({' + ','.join ('{' + ','.join (f'{expr ()}' for j in range (cols)) + ',}' for i in range (randrange (1, 4))) + ',})'

def expr_piece ():
	p = [f'{expr ()} if {expr ()}']

	for _ in range (randrange (3)):
		p.append (f'else {expr ()} if {expr ()}')

	if random () >= 0.5:
		p.append (f'else {expr ()}')

	return ' '.join (p)

def expr_lamb ():
	return f'lambda{choice (["", " x", " x, y", " x, y, z"])}: {expr ()}'

EXPRS = [va [1] for va in filter (lambda va: va [0] [:5] == 'expr_', globals ().items ())]

def expr (depth = None):
	global DEPTH, CURLYS

	if depth is not None:
		DEPTH = depth

	if not DEPTH:
		ret = choice (TERMS)

	else:
		DEPTH -= 1
		ret    = choice (EXPRS) ()
		DEPTH += 1

	return f'{{{ret}}}' if CURLYS else ret

def fix_vars (ast):
	if not isinstance (ast, AST):
		return ast

	if ast == ('@', '_'):
		return AST ('@', 'x')

	return AST (*tuple (fix_vars (a) for a in ast))

def process (ast):
	if not isinstance (ast, AST):
		return ast

	if ast.is_partial:
		return ast.as_diff

	if ast.is_paren:
		return process (ast.paren)

	return AST (*tuple (process (a) for a in ast))

def flatten (ast):
	if not isinstance (ast, AST):
		return ast

	t = [flatten (a) for a in ast]

	if ast.op in {'+', '*'}:
		t = (ast.op, tuple (sum (((m,) if m.op != ast.op else m [1] for m in t [1]), ())))

	return AST (*t)

#...............................................................................................
CURLYS = True
_DEPTH = 3

# test_sym.py -tnpi --show --nc

def test ():
	global CURLYS
	opts, _ = getopt (sys.argv [1:], 'tnpi', ['tex', 'nat', 'py', 'dump', 'show', 'inf', 'infinite', 'nc', 'nocurlys'])
	parser  = sparser.Parser ()

	if ('--dump', '') in opts:
		global DEPTH

		DEPTH = 0

		for e in EXPRS:
			print (e ())

		sys.exit (0)

	dotex  = ('--tex', '') in opts or ('-t', '') in opts
	donat  = ('--nat', '') in opts or ('-n', '') in opts
	dopy   = ('--py', '') in opts or ('-p', '') in opts
	CURLYS = not (('--nc', '') in opts or ('--nocurlys', '') in opts)

	if ('-i', '') in opts or ('--inf', '') in opts or ('--infinite', '') in opts:
		expr_func = lambda: expr (_DEPTH)
	else:
		expr_func = iter (_EXPRESSIONS).__next__

	try:
		while 1:
			text              = expr_func ()
			ast, erridx, auto = parser.parse (text)

			if not ast or erridx or auto:
				print ()
				print ('Invalid:', text)
				continue

			ast = flatten (ast)

			if ('--show', '') in opts:
				print ()
				print ('-' * 78)
				print ()
				print ('text:', text)

			if dopy:
				if not CURLYS:
					ast = fix_vars (ast)

				text              = sym.ast2py (ast)
				ast, erridx, auto = parser.parse (text)

				if not ast or erridx or auto:
					print ()
					print ('Invalid:', text)
					continue

			tex = dotex and sym.ast2tex (ast)
			nat = donat and sym.ast2nat (ast)
			py  = dopy and sym.ast2py (ast)

			if ('--show', '') in opts:
				print ()
				print ('text:', text)
				print ()
				print ('ast: ', ast)
				print ()
				print ('tex: ', tex)
				print ()
				print ('nat: ', nat)
				print ()
				print ('py:  ', py)

			ast_tex = dotex and parser.parse (tex) [0]
			ast_nat = donat and parser.parse (nat) [0]
			ast_py  = dopy and parser.parse (py) [0]
			ast_srp = process (ast)
			ast_tex = dotex and process (ast_tex)
			ast_nat = donat and process (ast_nat)
			ast_py  = dopy and process (ast_py)

			if (dotex and ast_tex != ast_srp) or (donat and ast_nat != ast_srp) or (dopy and ast_py != ast_srp):
				print ()
				print ('!' * 78)
				print ('text:', text)
				print ()
				print ('ast: ', ast_srp)

				if dotex and ast_tex != ast_srp:
					print ()
					print ('tex: ', ast_tex)

				if donat and ast_nat != ast_srp:
					print ()
					print ('nat: ', ast_nat)

				if dopy and ast_py != ast_srp:
					print ()
					print ('py:  ', ast_py)

				print ()
				print ('FOUND ONE!')

				sys.exit (0)

	except (Exception, KeyboardInterrupt) as e:
		print ()
		print ('!' * 78)
		print ('text:   ', text)
		print ('ast:    ', ast)
		print ('ast_srp:', ast_srp)
		print ('ast_tex:', ast_tex)
		print ('ast_nat:', ast_nat)
		print ('ast_py: ', ast_py)
		print ()

		if isinstance (e, StopIteration):
			print ("ALL GOOD...")
		elif not isinstance (e, KeyboardInterrupt):
			raise

if __name__ == '__main__':
	# parser = sparser.Parser ()
	# ast = parser.parse ("{{\\lim_{x \\to {{oo},}} {\\frac{d}{d}}}  {{{{{partialx} \\cdot {a'}}} \\cdot {{{a'}*{'str'}}}}}}") [0]
	# ast = parser.parse ('{{1+{2+3}}+4}') [0]
	# print (ast)
	# ast = flatten (ast)
	# print (ast)
	test ()

# (Matrix([[Derivative(a, y, 3, x, 2, x, 2) <= oo*1.0, Piecewise((oo, 0), (partialx = lambda: oo, lambda x, y, z: a_prime / {1.0 * {-1.0} d}, True))]]))
# x, y = lambda: 1, lambda: 2