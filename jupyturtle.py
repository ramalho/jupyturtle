import math
import time
from dataclasses import dataclass
from textwrap import dedent
from typing import NamedTuple

from IPython.display import display, HTML, DisplayHandle


# defaults
CANVAS_WIDTH = 400
CANVAS_HEIGHT = CANVAS_WIDTH // 2
CANVAS_BGCOLOR = '#FFF'

CANVAS_SVG = dedent(
    """
<svg width="{width}" height="{height}">
    <rect width="100%" height="100%" fill="{bgcolor}" />

    {contents}

</svg>
"""
).rstrip()


@dataclass
class Canvas:
    width: int = CANVAS_WIDTH
    height: int = CANVAS_HEIGHT
    bgcolor: str = CANVAS_BGCOLOR
    handle: DisplayHandle | None = None

    def get_SVG(self, contents):
        return CANVAS_SVG.format(
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
        style="stroke:{color};stroke-width:{width}"/>
"""
).rstrip()


class Line(NamedTuple):
    p1: Point
    p2: Point
    color: str
    width: int

    def get_SVG(self):
        (x1, y1), (x2, y2) = self.p1, self.p2
        return LINE_SVG.format(
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
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
TURTLE_COLOR = '#777'
TURTLE_HEADING = 0.0
PEN_COLOR = '#000'
PEN_WIDTH = 2

TURTLE_SVG = dedent(
    """
    <g id="{id}" transform="rotate({heading},{x},{y}) translate({x}, {y})">
        <circle stroke="{color}" stroke-width="2" fill="transparent" r="5.5" cx="0" cy="0"/>
        <polygon points="0,12 2,9 -2,9" style="fill:{color};stroke:{color};stroke-width:2"/>
    </g>
"""
).rstrip()


class Turtle:
    def __init__(self, delay: int = 0, canvas: Canvas | None = None):
        self.canvas = canvas if canvas else Canvas()
        self.position = Point(self.canvas.width // 2, self.canvas.height // 2)
        self.heading = TURTLE_HEADING
        self.color = TURTLE_COLOR
        self.visible = True
        self.active_pen = True
        self.pen_color = PEN_COLOR
        self.pen_width = PEN_WIDTH
        self.lines: list[Line] = []
        self.delay = delay
        self.init_vertices()
        self.display()

    @property
    def x(self) -> float:
        return self.position.x

    @property
    def y(self) -> float:
        return self.position.y

    def init_vertices(self):
        self.vertices = [self.position]

    def get_SVG(self):
        svg = []
        if self.visible:
            svg.append(
                TURTLE_SVG.format(
                    id=f'turtle{id(self):x}',
                    x=self.x,
                    y=self.y,
                    heading=self.heading - 90,
                    color=self.color,
                )
            )
        for line in self.lines:
            svg.append(line.get_SVG())

        return self.canvas.get_SVG('\n'.join(svg))

    def display(self):
        self.canvas.handle = display(HTML(self.get_SVG()), display_id=True)

    def update(self):
        if self.delay:
            time.sleep(self.delay)
        self.canvas.handle.update(HTML(self.get_SVG()))

    @command
    def hide(self):
        self.visible = False
        self.update()

    @command
    def show(self):
        self.visible = True
        self.update()

    @command_alias('fd')
    def forward(self, units: int):
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
        self.update()

    @command_alias('lt')
    def left(self, degrees: float):
        self.heading -= degrees
        self.update()

    @command_alias('rt')
    def right(self, degrees: float):
        self.heading += degrees
        self.update()

    @command
    def penup(self):
        self.active_pen = False

    @command
    def pendown(self):
        self.active_pen = True


################################################## procedural API

# _install_command() will append more names when the module loads
__all__ = ['Turtle', 'make_turtle']


def __dir__():
    return sorted(__all__)


main_turtle = None


def make_turtle(delay=0):
    global main_turtle
    main_turtle = Turtle(delay)


def _get_turtle():
    global main_turtle
    if not main_turtle:
        main_turtle = Turtle()
    return main_turtle


def _make_command(name):
    def command(*args):
        turtle = _get_turtle()
        getattr(turtle, name)(*args)

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
