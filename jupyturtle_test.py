from jupyturtle import Turtle, Point


def test_start_position():
    t = Turtle()
    assert t.position == Point(t.drawing.width // 2, t.drawing.height // 2)


def test_forward():
    t = Turtle()
    pos0 = t.position
    d = 100
    t.forward(d)
    pos1 = Point(pos0.x + d, pos0.y)
    assert t.position == pos1


def test_forward_right_square():
    t = Turtle()
    pos0 = t.position
    head0 = t.heading
    d = 42
    sides = 4
    for _ in range(sides):
        t.forward(d)
        t.right(90)
    assert t.position == pos0
    assert t.heading == head0


def test_forward_left_forward():
    t = Turtle()
    pos0 = t.position
    d = 50
    a, sin_a = 60, (3**0.5) / 2
    pos1 = pos0.translated(d + d / 2 / 2, -sin_a * d / 2)
    t.forward(d)
    t.left(a)
    t.forward(d / 2)
    assert t.heading == 360 - a
    assert t.position == pos1
