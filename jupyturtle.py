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
    x: int = 0
    y: int = 0

    def translated(self, dx: float, dy: float):
        return Point(round(self.x + dx), round(self.y + dy))


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


commands = {}


def command(method):
    commands[method.__name__] = method

    def inner(self, *args):
        method(self, *args)
        self.update()

    return inner


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
    def __init__(self, canvas: Canvas | None = None):
        self.canvas = canvas if canvas else Canvas()
        self.position = Point(self.canvas.width // 2, self.canvas.height // 2)
        self.heading = TURTLE_HEADING
        self.color = TURTLE_COLOR
        self.visible = True
        self.active_pen = True
        self.pen_color = PEN_COLOR
        self.pen_width = PEN_WIDTH
        self.lines: list[Line] = []
        self.delay = 0
        self.init_vertices()
        self.display()

    @property
    def x(self) -> int:
        return self.position.x

    @property
    def y(self) -> int:
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

    @command
    def show(self):
        self.visible = True

    @command
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

    @command
    def left(self, degrees: float):
        self.heading -= degrees

    @command
    def right(self, degrees: float):
        self.heading += degrees

    def penup(self):
        self.active_pen = False

    def pendown(self):
        self.active_pen = True


# procedural API

# TODO: refactor this reduce duplication

main_turtle = None


def get_turtle():
    global main_turtle
    if not main_turtle:
        main_turtle = Turtle()
    return main_turtle


def make_turtle(delay=0):
    global main_turtle
    main_turtle = Turtle()
    if delay:
        main_turtle.delay = delay


def forward(units):
    get_turtle().forward(units)


def left(degrees):
    get_turtle().left(degrees)


def right(degrees):
    get_turtle().right(degrees)


def hide():
    get_turtle().hide()


def show():
    get_turtle().show()


def penup():
    get_turtle().penup()

def pendown():
    get_turtle().pendown()


ALIASES = dict(
    fd=forward,
    lt=left,
    rt=right,
)

globals().update(ALIASES)
