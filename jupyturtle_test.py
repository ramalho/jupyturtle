from jupyturtle import Turtle, Point

def test_canvas_exists():
    # check that we can make a turtle and it has a canvas
    t = Turtle()
    assert t.canvas.get_SVG('').startswith('<svg')


def test_forward():
    t = Turtle()
    assert t.lines == []
    d = 100
    t.forward(d)
    p1 = Point(t.canvas.width // 2, t.canvas.height // 2)
    p2 = Point(p1.x + d, p1.y)
    assert t.lines[0].p1 == p1
    assert t.lines[0].p2 == p2


def test_forward_right_square():
    t = Turtle()
    pos = t.position
    heading = t.heading
    d = 42
    sides = 4
    for _ in range(sides):
        t.forward(d)
        t.right(90)
    assert t.position == pos
    assert t.heading == heading
    assert len(t.lines) == 4


def test_forward_left_forward():
    t = Turtle()
    d = 50
    a, sin_a = 60, (3**0.5) / 2
    t.forward(d)
    t.left(a)
    t.forward(d / 2)
    assert len(t.lines) == 2
    p1 = Point(t.canvas.width // 2 + d, t.canvas.height // 2)
    p2 = Point(p1.x + d / 2 / 2, p1.y - sin_a * d / 2)
    assert t.lines[1].p1 == p1
    assert t.lines[1].p2 == p2


