"""
🐢 jupyturtle.py release 2024-03-25
Celebrating the third edition of Think Python 🐍
"""

import math
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from textwrap import dedent
from typing import NamedTuple

from IPython.display import display, HTML, DisplayHandle


# defaults
DEFAULT_DRAW_WIDTH = 300
DEFAULT_DRAW_HEIGHT = 150
DRAW_BGCOLOR = '#F3F3F7'  # "anti-flash white" (non-standard name)


DRAW_SVG = dedent(
    """
<svg width="{width}" height="{height}" style="fill:none; stroke-linecap:round;">
    <rect width="100%" height="100%" fill="{bgcolor}" />

{contents}

</svg>
"""
).strip()


@dataclass
class Drawing:
    width: int = DEFAULT_DRAW_WIDTH
    height: int = DEFAULT_DRAW_HEIGHT
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


PATH_SVG = dedent(
    """
   <path stroke="{color}" stroke-width="{width}" d="{path}" />'

"""
).rstrip()


class Path(NamedTuple):
    points: list[Point]
    color: str
    width: int

    def append(self, point: Point):
        self.points.append(point)

    def __len__(self):
        return len(self.points)

    def get_SVG(self):
        path = 'M ' + ' '.join(
            [f'{round(point.x,1):g},{round(point.y,1):g}' for point in self.points]
        )
        return PATH_SVG.format(color=self.color, width=self.width, path=path)


# mapping of method names to global aliases
_commands = {}


# decorators to build procedural API with turtle commands
def command(method):
    """register method for use as a top level function in procedural API"""
    _commands[method.__name__] = []  # no alias
    return method


def command_alias(*names):
    """same as @command, but assigning aliases to the top level function"""

    def decorator(method):
        _commands[method.__name__] = list(names)
        return method

    return decorator


# defaults
TURTLE_HEADING = 0.0  # pointing to screen left, a.k.a. "east"
TURTLE_COLOR = '#63A375'  # "mint" (non-standard name)
TURTLE_DELAY = 0.2  # pause after each visual command, in seconds
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
        self,
        *,
        auto_render=True,
        delay: float | None = None,
        drawing: Drawing | None = None,
    ):
        self.auto_render = auto_render
        self.delay = delay
        self.drawing = drawing if drawing else Drawing()
        self.position = Point(self.drawing.width // 2, self.drawing.height // 2)
        self.heading = TURTLE_HEADING
        self.color = TURTLE_COLOR
        self.visible = True
        self.active_pen = True
        self.__pen_color = PEN_COLOR
        self.__pen_width = PEN_WIDTH
        self.paths: list[Path] = [
            Path(points=[self.position], color=PEN_COLOR, width=PEN_WIDTH)
        ]
        # TODO: issue warning if `display` did not return a handle
        self.drawing.handle = display(HTML(self.get_SVG()), display_id=True)

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

    @property
    def pen_color(self):
        return self.__pen_color

    @pen_color.setter
    def pen_color(self, color):
        if color == self.__pen_color:
            return
        self.__pen_color = color
        new_path = Path(points=[self.position], color=color, width=self.pen_width)
        # create new path if there is no current path or if the current path has points
        if not self.paths or len(self.paths[-1]) > 1:
            self.paths.append(new_path)
        else:  # otherwise, replace the current empty path
            self.paths[-1] = new_path

    @property
    def pen_width(self):
        return self.__pen_width

    @pen_width.setter
    def pen_width(self, width):
        if width == self.__pen_width:
            return
        self.__pen_width = width
        new_path = Path(points=[self.position], color=self.pen_color, width=width)
        # create new path if there is no current path or if the current path has points
        if not self.paths or len(self.paths[-1]) > 1:
            self.paths.append(new_path)
        else:  # otherwise, replace the current empty path
            self.paths[-1] = new_path

    @property
    def delay(self):
        return self.__delay

    @delay.setter
    def delay(self, s):
        if s is None:
            self.__delay = TURTLE_DELAY
            return
        if s == 0:
            self.__delay = 0
            return
        if not self.auto_render:
            print('Warning: delay is ignored when auto_render=False', file=sys.stderr)
        self.__delay = s

    def get_SVG(self):
        svg = [path.get_SVG() for path in self.paths]
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

    @command
    def render(self):
        # TODO: issue warning if `handle` is None
        if h := self.drawing.handle:
            if self.delay and self.auto_render:
                time.sleep(self.delay)
            h.update(HTML(self.get_SVG()))

    @command
    def hide(self):
        """Hide turtle. It will still leave trail if the pen is down."""
        self.visible = False
        # every method that changes the drawing must:
        if self.auto_render:  # check if auto_render is enabled
            self.render()  # if so, update the display

    @command
    def show(self):
        """Show turtle."""
        self.visible = True
        if self.auto_render:
            self.render()

    @command
    def moveto(self, x: float, y: float):
        """Move the turtle to coordinates (x, y), drawing if the pen is down."""
        new_pos = Point(x, y)
        if self.active_pen:
            self.paths[-1].append(Point(*new_pos))
        else:
            self.paths.append(
                Path(points=[new_pos], color=self.pen_color, width=self.pen_width)
            )
        self.position = new_pos
        if self.auto_render:
            self.render()

    @command_alias('fd')
    def forward(self, units: float):
        """Move turtle forward by units; draw path if pen is down."""
        angle = math.radians(self.heading)
        dx = units * math.cos(angle)
        dy = units * math.sin(angle)
        new_pos = self.position.translated(dx, dy)
        self.moveto(*new_pos)

    @command_alias('bk')
    def back(self, units: float):
        """Move the turtle backward by units, drawing if the pen is down."""
        self.forward(-units)

    @command
    def jumpto(self, x: float, y: float):
        """Teleport the turtle to coordinates (x, y) without drawing."""
        self.position = Point(x, y)
        self.paths.append(
            Path(points=[self.position], color=self.pen_color, width=self.pen_width)
        )
        if self.auto_render:
            self.render()

    @command_alias('lt')
    def left(self, degrees: float):
        """Turn turtle left by degrees."""
        self.heading -= degrees
        if self.auto_render:
            self.render()

    @command_alias('rt')
    def right(self, degrees: float):
        """Turn turtle right by degrees."""
        self.heading += degrees
        if self.auto_render:
            self.render()

    @command
    def penup(self):
        """Lift the pen, so turtle stops drawing."""
        self.active_pen = False

    @command
    def pendown(self):
        """Lower the pen, so turtle starts drawing."""
        self.active_pen = True

    @command
    def toggle_pen(self):
        """Lower the pen if it's up; raises if it's down."""
        self.active_pen = not self.active_pen

    def __enter__(self):
        self.saved_auto_render = self.auto_render
        self.auto_render = False
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.auto_render = self.saved_auto_render
        if self.auto_render:
            self.render()


################################################## procedural API

# _install_command() will append more names when the module loads
__all__ = [
    'Turtle',
    'make_turtle',
    'get_turtle',
    'no_pen',
    'set_color',
    'set_width',
    'no_update',
    'set_default',
    'set_heading',
    'show_SVG',
]


def __dir__():
    return sorted(__all__)


_main_turtle = None


def make_turtle(
    *, auto_render=True, delay=None, width=DEFAULT_DRAW_WIDTH, height=DEFAULT_DRAW_HEIGHT
) -> Turtle:
    """Makes new Turtle and sets _main_turtle."""
    global _main_turtle
    drawing = Drawing(width=width, height=height)
    _main_turtle = Turtle(auto_render=auto_render, delay=delay, drawing=drawing)
    return _main_turtle


def get_turtle() -> Turtle:
    """Gets existing _main_turtle; makes one if needed."""
    global _main_turtle
    if _main_turtle is None:
        _main_turtle = Turtle()
    return _main_turtle


def set_color(color: str):
    """Set the pen color."""
    turtle = get_turtle()
    turtle.pen_color = color


def set_width(width: int):
    """Set the pen width."""
    turtle = get_turtle()
    turtle.pen_width = width


def set_heading(angle: float):
    """Set turtle heading: 0 is right, 90 is up etc."""
    turtle = get_turtle()
    turtle.heading = angle


@contextmanager
def no_pen():
    turtle = get_turtle()
    pen_state = turtle.active_pen
    turtle.penup()
    yield
    if pen_state:
        turtle.pendown()


@contextmanager
def no_update():
    with get_turtle() as t:
        yield


def set_default(**kwargs):
    """set new value for all-caps “CONSTANTS”"""
    for name, value in kwargs.items():
        if name != name.upper():
            raise ValueError('Argument names must be UPPER_CASE.')
        globals()[name] = value

def show_SVG():
    print(get_turtle().get_SVG())

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
