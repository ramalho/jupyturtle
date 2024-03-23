# jupyturtle

Python Turtle graphics for Jupyter notebooks

For a quick demo, open [the lab notebook](lab.ipynb).

No installation required, just download the `jupyter.py`
module to the same folder where your notebook is saved,
and import it.


## Credits

The idea and some of the code for this module came from
[Tolga Atam](https://github.com/tolgaatam)'s
[ColabTurtle](https://github.com/tolgaatam/ColabTurtle/tree/master),
which I discovered reading a pre-print version of
[Allen Downey](https://github.com/allendowney)'s book
_[Think Python, Third Edition](https://greenteapress.com/wp/think-python-3rd-edition/)_ (O'Reilly, 2024).


## Design

Atam's best idea was to use SVG for drawing, which makes the code simple and lightweight, 
requiring only the Python standard library and the
`ipython` module that is always available in Jupyter.

This is a rewrite from scratch, using classes to model the turtle
and the drawing.
My goal was to make it easier to understand and extend by
encapsulating the state.

I used metaprogramming techniques to build the procedural API
with global functions like `fd()` to move the turtle.
The techniques are easier to understand in the didactic project
[abacus](https://github.com/fluentpython/abacus).

### Turtle on a canvas

[`jupyturtle2`](https://github.com/fluentpython/jupyturtle2) is a fork
that uses 
[`ipycanvas`](https://ipycanvas.readthedocs.io/en/latest/)
to draw pixels on an HTML canvas, instead of generating SVG,
so it handles complex drawings better.

But `jupyturtle2` has two main drawbacks:

* `ipycanvas` requires the binary dependencies `numpy` and `pillow`,
which may be harder to install in some environments.

* the generated drawings are not saved with the notebook like most other output cells; this is also a limitation of `ipycanvas`

*[@ramalho](https://github.com/ramalho)*
