import math
import time
from dataclasses import dataclass
from textwrap import dedent
from typing import NamedTuple

from IPython.display import display
from ipycanvas import MultiCanvas

# defaults
CANVAS_WIDTH = 400
CANVAS_HEIGHT = CANVAS_WIDTH // 2
CANVAS_BGCOLOR = '#F3F3F7'  # "anti-flash white" (non-standard name)


class Point(NamedTuple):
    x: float = 0
    y: float = 0

    def translated(self, dx: float, dy: float):
        return Point(self.x + dx, self.y + dy)


class Line(NamedTuple):
    p1: Point
    p2: Point
    color: str
    width: int


# mapping of method names to global aliases
_commands = {}


# decorators to build procedural API with turtle commands
def command(method):
    """register method for use as a top level function in procedural API"""
    _commands[method.__name__] = []  # no alias
    return method


def command_alias(*names):
    def decorator(method):
        _commands[method.__name__] = list(names)
        return method

    return decorator


# defaults
TURTLE_HEADING = 0.0  # pointing to screen left, a.k.a. "east"
TURTLE_COLOR = '#63A375'  # "mint" (non-standard name)
TURTLE_THICKNESS = 2  # width of circle stroke
TURTLE_DELAY = 0.01  # seconds between turtle actions
PEN_COLOR = '#663399'  # rebeccapurple https://www.w3.org/TR/css-color-4/#valdef-color-rebeccapurple
PEN_WIDTH = 2

TURTLE_SVG = dedent(
    """
    <g transform="rotate({heading},{x},{y}) translate({x}, {y})">
        <circle stroke="{color}" stroke-width="2" fill="transparent" r="5.5" cx="0" cy="0"/>
        <polygon points="0,12 2,9 -2,9" style="fill:{color};stroke:{color};stroke-width:2"/>
    </g>
"""
).rstrip()


class Turtle:
    def __init__(self, *, delay: float = TURTLE_DELAY, canvas: MultiCanvas | None = None):
        self.delay = delay
        self.canvas = canvas if canvas else MultiCanvas(3, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        try:
            self.background = self.canvas[0]
            self.drawing = self.canvas[1]
            self.foreground = self.canvas[2]
        except IndexError:
            raise ValueError('MultiCanvas must have at least 3 layers')
        self.position = Point(self.canvas.width // 2, self.canvas.height // 2)
        self.heading = TURTLE_HEADING
        self.color = TURTLE_COLOR
        self.visible = True
        self.pen_is_down = True
        self.pen_color = PEN_COLOR
        self.pen_width = PEN_WIDTH
        self.prepare_layers()
        self.draw()
        display(self.canvas)

    def prepare_layers(self):
        """setup canvas layers"""
        self.background.fill_style = CANVAS_BGCOLOR
        self.background.fill_rect(0, 0, self.canvas.width, self.canvas.height)
        # drawing layer
        self.drawing.line_width = self.pen_width
        self.drawing.stroke_style = self.pen_color

    @property
    def x(self) -> float:
        return self.position.x

    @property
    def y(self) -> float:
        return self.position.y

    @property
    def heading(self) -> float:
        return self.__heading

    @heading.setter
    def heading(self, new_heading) -> None:
        self.__heading = new_heading % 360.0

    def draw(self):
        """Draw the turtle."""
        x, y = self.x, self.y
        self.foreground.line_width = TURTLE_THICKNESS
        self.foreground.stroke_style = self.color
        self.foreground.fill_style = self.color
        head_x = x + 7.5 * math.cos(math.radians(self.heading))
        head_y = y + 7.5 * math.sin(math.radians(self.heading))
        self.foreground.clear()
        self.foreground.stroke_circle(x+.5, y+.5, 5)
        self.foreground.stroke_circle(head_x, head_y, 1)


    @command
    def hide(self):
        """Hide the turtle. It will still draw, but you won't see it."""
        self.visible = False
        self.foreground.clear()

    @command
    def show(self):
        """Show the turtle."""
        self.visible = True
        self.draw()

    @command_alias('fd')
    def forward(self, units: float):
        """Move the turtle forward by units, drawing if the pen is down."""
        angle = math.radians(self.heading)
        dx = units * math.cos(angle)
        dy = units * math.sin(angle)
        new_pos = self.position.translated(dx, dy)
        if self.pen_is_down:
            self.drawing.stroke_line(self.x, self.y, new_pos.x, new_pos.y)
        self.position = new_pos
        self.draw()
        if self.delay:
            time.sleep(self.delay)

    @command_alias('lt')
    def left(self, degrees: float):
        """Turn the turtle left by degrees."""
        self.heading -= degrees
        self.draw()
        if self.delay:
            time.sleep(self.delay)

    @command_alias('rt')
    def right(self, degrees: float):
        """Turn the turtle right by degrees."""
        self.heading += degrees
        self.draw()
        if self.delay:
            time.sleep(self.delay)

    @command
    def penup(self):
        """Lift the pen, so the turtle leaves no trail."""
        self.pen_is_down = False

    @command
    def pendown(self):
        """Lower the pen, so the turtle leaves a trail."""
        self.pen_is_down = True


################################################## procedural API

# _install_command() will append more names when the module loads
__all__ = ['Turtle', 'make_turtle', 'get_turtle']


def __dir__():
    return sorted(__all__)


_main_turtle = None


def make_turtle(*, delay=TURTLE_DELAY) -> None:
    """Makes new Turtle and sets _main_turtle."""
    global _main_turtle
    _main_turtle = Turtle(delay=delay)


def get_turtle() -> Turtle:
    """Gets existing _main_turtle; makes one if needed."""
    global _main_turtle
    if _main_turtle is None:
        _main_turtle = Turtle()
    return _main_turtle


def _make_command(name):
    method = getattr(Turtle, name)  # get unbound method

    def command(*args):
        turtle = get_turtle()
        method(turtle, *args)

    command.__name__ = name
    command.__doc__ = method.__doc__
    return command


def _install_command(name, function):
    if name in globals():
        raise ValueError(f'duplicate turtle command name: {name}')
    globals()[name] = function
    __all__.append(name)


def _install_commands():
    for name, aliases in _commands.items():
        new_command = _make_command(name)
        _install_command(name, new_command)
        for alias in aliases:
            _install_command(alias, new_command)


_install_commands()
