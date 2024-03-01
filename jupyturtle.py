import math
import time
from dataclasses import dataclass
from textwrap import dedent
from typing import NamedTuple

from IPython.display import display, HTML, DisplayHandle


# defaults
DRAW_WIDTH = 400
DRAW_HEIGHT = DRAW_WIDTH // 2
DRAW_BGCOLOR = '#F3F3F7'  # "anti-flash white" (non-standard name)


DRAW_SVG = dedent(
    """
<svg width="{width}" height="{height}">
    <rect width="100%" height="100%" fill="{bgcolor}" />

{contents}

</svg>
"""
).strip()


@dataclass
class Drawing:
    width: int = DRAW_WIDTH
    height: int = DRAW_HEIGHT
    bgcolor: str = DRAW_BGCOLOR
    handle: DisplayHandle | None = None

    def get_SVG(self, contents):
        return DRAW_SVG.format(
            width=self.width,
            height=self.height,
            bgcolor=self.bgcolor,
            contents=contents,
        )


class Point(NamedTuple):
    x: float = 0
    y: float = 0

    def translated(self, dx: float, dy: float):
        return Point(self.x + dx, self.y + dy)


LINE_SVG = dedent(
    """
    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke-linecap="round"
      style="stroke:{color};stroke-width:{width}" />"""
).strip()


class Line(NamedTuple):
    p1: Point
    p2: Point
    color: str
    width: int

    def get_SVG(self):
        (x1, y1), (x2, y2) = self.p1, self.p2
        return LINE_SVG.format(
            x1=round(x1, 1),
            y1=round(y1, 1),
            x2=round(x2, 1),
            y2=round(y2, 1),
            color=self.color,
            width=self.width,
        )


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
    def __init__(
        self, *, auto_draw=True, delay: float = 0, drawing: Drawing | None = None
    ):
        self.auto_draw = auto_draw
        self.delay = delay
        self.drawing = drawing if drawing else Drawing()
        self.position = Point(self.drawing.width // 2, self.drawing.height // 2)
        self.heading = TURTLE_HEADING
        self.color = TURTLE_COLOR
        self.visible = True
        self.active_pen = True
        self.pen_color = PEN_COLOR
        self.pen_width = PEN_WIDTH
        self.lines: list[Line] = []
        self.display()

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

    def get_SVG(self):
        svg = []
        for line in self.lines:
            svg.append(line.get_SVG())
        if self.visible:
            svg.append(
                TURTLE_SVG.format(
                    id=f'turtle{id(self):x}',
                    x=round(self.x, 1),
                    y=round(self.y, 1),
                    heading=round(self.heading - 90, 1),
                    color=self.color,
                )
            )

        return self.drawing.get_SVG('\n'.join(svg))

    def display(self):
        # TODO: issue warning if `display` did not return a handle
        self.drawing.handle = display(HTML(self.get_SVG()), display_id=True)

    @command
    def update(self):
        # TODO: issue warning if `handle` is None
        if h := self.drawing.handle:
            if self.delay and self.auto_draw:
                time.sleep(self.delay)
            h.update(HTML(self.get_SVG()))

    @command
    def hide(self):
        """Hide the turtle. It will still draw, but you won't see it."""
        self.visible = False
        # every method that changes the drawing must:
        if self.auto_draw:  # check if auto_draw is enabled
            self.update()  # if so, update the display

    @command
    def show(self):
        """Show the turtle."""
        self.visible = True
        if self.auto_draw:
            self.update()

    @command_alias('fd')
    def forward(self, units: float):
        """Move the turtle forward by units, drawing if the pen is down."""
        angle = math.radians(self.heading)
        dx = units * math.cos(angle)
        dy = units * math.sin(angle)
        new_pos = self.position.translated(dx, dy)
        if self.active_pen:
            self.lines.append(
                Line(
                    p1=self.position,
                    p2=new_pos,
                    color=self.pen_color,
                    width=self.pen_width,
                )
            )
        self.position = new_pos
        if self.auto_draw:
            self.update()

    @command_alias('lt')
    def left(self, degrees: float):
        """Turn the turtle left by degrees."""
        self.heading -= degrees
        if self.auto_draw:
            self.update()

    @command_alias('rt')
    def right(self, degrees: float):
        """Turn the turtle right by degrees."""
        self.heading += degrees
        if self.auto_draw:
            self.update()

    @command
    def penup(self):
        """Lift the pen, so the turtle stops drawing."""
        self.active_pen = False

    @command
    def pendown(self):
        """Lower the pen, so the turtle starts drawing."""
        self.active_pen = True

    def __enter__(self):
        self.saved_auto_draw = self.auto_draw
        self.auto_draw = False
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.auto_draw = self.saved_auto_draw
        if self.auto_draw:
            self.update()


################################################## procedural API

# _install_command() will append more names when the module loads
__all__ = ['Turtle', 'make_turtle', 'get_turtle']


def __dir__():
    return sorted(__all__)


_main_turtle = None


def make_turtle(
    *, auto_draw=True, delay=0, width=DRAW_WIDTH, height=DRAW_HEIGHT
) -> None:
    """Makes new Turtle and sets _main_turtle."""
    global _main_turtle
    drawing = Drawing(width=width, height=height)
    _main_turtle = Turtle(auto_draw=auto_draw, delay=delay, drawing=drawing)


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
