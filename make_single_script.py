#!/usr/bin/env python
# python 3.6+

# Collect all source and data files into single sympad.py script file.

_PY_FILES    = ('lalr1.py', 'sast.py', 'sparser.py', 'sym.py', 'server.py')
_OTHER_FILES = ('style.css', 'script.js', 'index.html', 'help.html')

_HEADER = '''
#!/usr/bin/env python
# python 3.6+

# Copyright (c) 2019 Tomasz Pytel
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

_RUNNING_AS_SINGLE_SCRIPT = True

'''.lstrip ()

if __name__ == '__main__':
	fdout = open ('sympad.py', 'w', newline = '')

	fdout.write (_HEADER)
	fdout.write ('\n_FILES = {\n')

	for fnm in _OTHER_FILES:
		fdout.write (f'''\n\t'{fnm}': # {fnm}\n\nr"""''')

		for line in open (fnm):
			fdout.write (line)

		fdout.write ('""".encode ("utf8"),\n')

	fdout.write ('}\n\n')

	for fnm in _PY_FILES:
		for line in open (fnm):
			if not line.rstrip ().endswith ('# AUTO_REMOVE_IN_SINGLE_SCRIPT'):
				fdout.write (line)
