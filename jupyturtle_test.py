import xml.etree.ElementTree as ET

from jupyturtle import Turtle, Point, PEN_COLOR, PEN_WIDTH


def test_drawing_exists():
    """we can make a turtle and get SVG from it"""
    t = Turtle()
    root = ET.fromstring(t.get_SVG())

    assert root.tag == 'svg'

def test_line_attributes():
    """line attributes must reflect turtle pen_color and pen_width"""
    t = Turtle()
    p0 = t.position
    t.forward(100)
    p1 = t.position
    t.pen_color = 'red'
    t.pen_width = 5
    t.right(90)
    t.forward(100)
    root = ET.fromstring(t.get_SVG())
    lines = root.findall(".//line")
    assert len(lines) == 2
    assert lines[0].attrib['x1'] == str(p0.x)
    assert lines[0].attrib['y1'] == str(p0.y)
    assert lines[0].attrib['x2'] == str(p1.x)
    assert lines[0].attrib['y2'] == str(p1.y)
    assert lines[0].attrib['color'] == PEN_COLOR
    assert lines[0].attrib['stroke-width'] == str(PEN_WIDTH)
    assert lines[-1].attrib['color'] == t.pen_color
    assert lines[-1].attrib['stroke-width'] == str(t.pen_width)
    root = ET.fromstring(t.get_SVG())
    lines = root.findall(".//line")[0]


def test_forward():
    t = Turtle()
    p1 = t.position
    assert t.lines == []
    d = 100
    t.forward(d)
    p2 = Point(p1.x + d, p1.y)
    assert t.lines[0].p1 == p1
    assert t.lines[0].p2 == p2


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
    assert len(t.lines) == 4


def test_forward_left_forward():
    t = Turtle()
    d = 50
    t.forward(d)
    p1 = t.position
    a, sin_a, cos_a = 60, (3**0.5) / 2, .5
    t.right(a)
    d2 = d / 2
    t.forward(d2)
    assert len(t.lines) == 2
    p2 = Point(p1.x + cos_a * d2, p1.y + sin_a * d2)
    assert t.lines[1].p1 == p1
    assert t.lines[1].p2 == p2
