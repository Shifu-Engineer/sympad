# SymPad

SymPad is a simple single script graphical symbolic calculator / scratchpad using SymPy for the math, MathJax for the display in a browser and matplotlib for plotting.
User input is intended to be quick, easy and intuitive and is displayed in symbolic form as it is being entered.
Sympad will accept Python expressions, LaTeX formatting, unicode math symbols and a native shorthand intended for quick entry, or a mix of all of these.
The input will be evaluated symbolically or numerically with the results being copy/pasteable in Python or LaTeX formats, so it acts as a translator as well.

The following are examples of valid inputs to SymPad:
```
cos**-1 0 + \log_2{8}
factor (x**3 + 3 y x**2 + 3 x y**2 + y**3)
series (e^x, x, 0, 5)
solve (x**2 + y = 4, x)
\lim_{x\to\infty} 1/x
\sum_{n=0}**oo x^n / n!
d**6 / dx dy**2 dz**3 x^3 y^3 z^3
\int_0^\pi \int_0^{2pi} \int_0^1 rho**2 sin\phi drho dtheta dphi
\[[1, 2], [3, 4]]**-1
Matrix ([[1, 2, 3], [4, 5, 6]]) [:,1].transpose ()
Matrix (4, 4, lambda r, c: c + r if c &gt; r else 0)
(({1, 2, 3} && {2, 3, 4}) ^^ {3, 4, 5}) - \{4} || {7,}
plot (2pi, -2, 2, sin x, 'r=sin', cos x, 'g=cos', tan x, 'b=tan')
```

And they look like this while typing:

![SymPad image example](https://raw.githubusercontent.com/Pristine-Cat/SymPad/master/sympad.png#1)

## Installation

In order to run this program you must have Python 3.6+ installed: [https://www.python.org/](https://www.python.org/)

Once Python is set up you need to install SymPy: [https://sympy.org/](https://sympy.org/)
```
pip install sympy
```

In order to get the optional plotting functionality you must have the matplotlib package installed: [https://matplotlib.org/](https://matplotlib.org/)
```
pip install matplotlib
```

Once those are installed, if you just want to use the program you only need the file **sympad.py**.
This is an autogenerated Python script which contains all the modules and web resources in one handy easily copyable file.

Otherwise if you want to play with the code then download everything and run the program using **server.py**.

If you want to regenerate the parser tables you will need the PLY Python package: [https://www.dabeaz.com/ply/](https://www.dabeaz.com/ply/)
```
pip install ply
```

## Open-Source License

SymPad is made available under the BSD license, you may use it as you wish, as long as you copy the BSD statement if you redistribute it. See the LICENSE file for details.
