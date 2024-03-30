import xml.etree.ElementTree as ET

from jupyturtle import Turtle, Point, Path
from jupyturtle import DEFAULT_DRAW_WIDTH, DEFAULT_DRAW_HEIGHT, PEN_COLOR, PEN_WIDTH


def test_drawing_exists():
    """we can make a turtle and get SVG from it"""
    t = Turtle()
    root = ET.fromstring(t.get_SVG())

    assert root.tag == 'svg'


def test_path_attributes():
    """path attributes must reflect turtle pen_color and pen_width"""
    t = Turtle()
    t.pen_color = 'red'
    t.pen_width = 5
    p0 = t.position
    t.forward(100)
    p1 = t.position
    root = ET.fromstring(t.get_SVG())
    paths = root.findall('.//path')
    assert len(paths) == 1
    expected = (
        f'M {round(p0.x,1):g},{round(p0.y,1):g} {round(p1.x,1):g},{round(p1.y,1):g}'
    )
    assert paths[0].attrib['d'] == expected
    assert paths[0].attrib['stroke'] == t.pen_color
    assert paths[0].attrib['stroke-width'] == str(t.pen_width)


def test_forward():
    t = Turtle()
    p1 = t.position
    start = Point(DEFAULT_DRAW_WIDTH // 2, DEFAULT_DRAW_HEIGHT // 2)
    assert len(t.paths) == 1
    assert t.paths[0] == Path([start], color=PEN_COLOR, width=PEN_WIDTH)
    d = 100
    t.forward(d)
    p2 = Point(p1.x + d, p1.y)
    assert len(t.paths) == 1
    assert len(t.paths[0].points) == 2
    assert t.paths[0].points[-1] == p2


def test_forward_right_square():
    t = Turtle()
    p1 = t.position
    heading = t.heading
    d = 42
    sides = 4
    for _ in range(sides):
        t.forward(d)
        t.right(90)
    assert t.position == p1
    assert t.heading == heading
    assert len(t.paths) == 1
    assert len(t.paths[0].points) == 5


def test_forward_left_forward():
    t = Turtle()
    d = 50
    t.forward(d)
    p1 = t.position
    a, sin_a, cos_a = 60, (3**0.5) / 2, 0.5
    t.right(a)
    d2 = d / 2
    t.forward(d2)
    assert len(t.paths) == 1
    p2 = Point(p1.x + cos_a * d2, p1.y + sin_a * d2)
    assert t.paths[0].points[1] == p1
    assert t.paths[0].points[2] == p2
