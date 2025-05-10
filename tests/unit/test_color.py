from uniplot.colors import Color


def test_init_color_from_param_with_terminal_name():
    param = "red"
    c = Color.from_param(param)

    assert c.is_enabled()
    assert len(c.colorize("x")) > 1


def test_init_color_from_param_with_rgb_values():
    param = (87, 120, 163)
    c = Color.from_param(param)

    assert c.is_enabled()
    assert len(c.colorize("x")) > 1
