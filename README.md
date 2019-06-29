# SymPad

SymPad is a simple symbolic calculator using SymPy for the math and MathJax for the display in a web browser. It runs as a private web server on your machine and executes the system default browser pointing to itself on startup.
User input is intended to be quick, easy and intuitive and is displayed in symbolic form as it is being entered.
Sympad will accept LaTeX math formatting as well as Python expressions (or a mix) and evaluate the result symbolically or numerically. The following are all valid inputs:
```
2*x**2
2x^2
sin (x) / cos (y)
\frac{\sin x}{\cos y}
sqrt[3] 27
\tan**{-1} x
\lim_{x \to 0^-} 1/x
\sum_{n=0}^\infty x**n / n!
d/dx x**2
\int_{-\infty}^\infty e**{-x**2} dx
```

## Installation

SymPad has one dependancy which must be installed on your system in order to run which is the SymPy Python package: [https://sympy.org/](https://sympy.org/).
Apart from that, if you just want to use the program you will only need the file **sympad.py**. This is an autogenerated Python script which contains all the modules (apart from SymPy) and web resources in one handy file.

Otherwise if you want to play with the code then download everything and run the program using **server.py**.

If you want to regenerate the parser tables you will need the PLY Python package: [https://www.dabeaz.com/ply/](https://www.dabeaz.com/ply/).

## Open-Source License

SymPad is made available under the BSD license, you may use it as you wish, as long as you copy the BSD statement if you redistribute it (see the LICENSE file for details).
