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


def test_init_color_from_param_with_hex_values():
    param = "#B4FBB8"
    c = Color.from_param(param)

    # Test conversion to RGB
    # Ref.: https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
    assert c.rgb == (180, 251, 184)

    assert c.is_enabled()
    assert len(c.colorize("x")) > 1
