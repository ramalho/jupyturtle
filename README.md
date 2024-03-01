# jupyturtle
Python Turtle graphics for Jupyter notebooks

For a quick demo, open [the lab notebook](lab.ipynb).

The idea and some of the code for this module was inspired by
[Tolga Atam](https://github.com/tolgaatam)'s
[ColabTurtle](https://github.com/tolgaatam/ColabTurtle/tree/master),
via [Allen Downey](https://github.com/allendowney)'s book
_Think Python, Third Edition_ (O'Reilly, 2024).

Atam's best idea was to use SVG for drawing, which makes the
code simple and lightweight, requiring no special dependencies
besides the `ipython` module that is always available in Jupyter.

This is a rewrite from scratch, using classes to model the turtle
and the drawing—to make it easier to test, maintain and evolve by
avoiding global variables to keep program state.

I created a fork—[jupyturtle2](https://github.com/fluentpython/jupyturtle2)—which
uses `ipycanvas` to draw on an HTML canvas, instead of generating SVG.
`ipycanvas` requires the binary dependencies `numpy` and `pillow`,
so it may be harder to deploy in some environments.
`jupyturtle2` is better than `jupyturtle` in some respects, but worse in others.

I used metaprogramming techniques to build the procedural API
with global functions like `fd()` to move the turtle.
The techniques are easier to understand in the didactic project
[abacus](https://github.com/fluentpython/abacus).


@ramalho
