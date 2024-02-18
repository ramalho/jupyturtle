import math
from typing import NamedTuple

from IPython.display import display, HTML, DisplayHandle


# defaults
CANVAS_WIDTH = 400
CANVAS_HEIGHT = CANVAS_WIDTH // 2
CANVAS_BGCOLOR = '#FFF'

CANVAS_SVG = """
    <svg width="{width}" height="{height}">
        <rect width="100%" height="100%" fill="{bgcolor}" />
        {contents}
    </svg>
"""


class Canvas:
    def __init__(
        self,
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT,
        bgcolor: str = CANVAS_BGCOLOR,
        handle: DisplayHandle|None = None
    ):
        self.width = width
        self.height = height
        self.bgcolor = bgcolor
        self.handle = handle

    def get_SVG(self, contents):
        return CANVAS_SVG.format(
            width=self.width,
            height=self.height,
            bgcolor=self.bgcolor,
            contents=contents,
        )


# defaults
TURTLE_COLOR = '#777'
TURTLE_HEADING = 0.0
PEN_COLOR = '#000'
PEN_WIDTH = 2

TURTLE_SVG = """
        <g transform="rotate({heading},{x},{y}) translate({x}, {y})">
        <circle stroke="{color}" stroke-width="2" fill="transparent" r="5.5" cx="0" cy="0"/>
        <polygon points="0,12 2,9 -2,9" style="fill:{color};stroke:{color};stroke-width:2"/>
        </g>
    """.strip()

LINE_SVG = """
    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke-linecap="round"
     style="stroke:{pen_color};stroke-width:{pen_width}"/>

"""


class Point(NamedTuple):
    x: int = 0
    y: int = 0


class Turtle:
    def __init__(self, canvas: Canvas | None = None):
        self.canvas = canvas if canvas else Canvas()
        self.position = Point(self.canvas.width // 2, self.canvas.height // 2)
        self.heading = TURTLE_HEADING
        self.color = TURTLE_COLOR
        self.visible = True
        self.waypoints: list[Point] = []
        self.init_waypoints()

    @property
    def x(self) -> int:
        return self.position.x

    @property
    def y(self) -> int:
        return self.position.y
    
    #@updater
    def hide(self):
        self.visible = False

    #@updater
    def show(self):
        self.visible = True


    def init_waypoints(self):
        self.waypoints = [self.position]

    def get_SVG(self):
        svg = []
        if self.visible:
            svg.append(
                TURTLE_SVG.format(
                    x=self.x, y=self.y, heading=self.heading-90, color=self.color
                )
            )
            while len(self.waypoints) >= 2:
                (x1, y1), (x2, y2) = self.waypoints[:2]
                svg.append(
                    LINE_SVG.format(
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2,
                        pen_color=PEN_COLOR,
                        pen_width=PEN_WIDTH,
                    )
                )
                del self.waypoints[0]
            self.init_waypoints()
        else:
            "XXX TODO"
        return self.canvas.get_SVG('\n'.join(svg))

    def display(self):
        self.canvas.handle = display(HTML(self.get_SVG()), display_id=True)

    def update(self):
        self.canvas.handle.update(HTML(self.get_SVG()))

    def forward(self, units: int):
        angle = math.radians(self.heading)
        self.position = Point(
            x = round(self.x + units * math.cos(angle)),
            y = round(self.y + units * math.sin(angle)),
        )
        self.waypoints.append(self.position)
        self.update()

    def left(self, degrees: float):
        self.heading -= degrees
        self.update


# procedural API

# TODO: refactor this reduce duplication

main_turtle = None

def forward(units):
    global main_turtle
    if not main_turtle:
        main_turtle = Turtle()
        main_turtle.display()
    main_turtle.forward(units)

def left(degrees):
    global main_turtle
    if not main_turtle:
        main_turtle = Turtle()
        main_turtle.display()
    main_turtle.left(degrees)


ALIASES = dict(
    fd = forward,
    lt = left,
)

globals().update(ALIASES)
