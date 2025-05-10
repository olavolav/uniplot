import re
from dataclasses import dataclass
from typing import Tuple, Optional, Any, Final


ANSI_COLOR_CODES: Final = {
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "red": "\033[31m",
}
DEFAULT_COLORS_NAMES: Final = list(ANSI_COLOR_CODES.keys())
DEFAULT_COLORS: Final = list(ANSI_COLOR_CODES.values())

COLOR_RESET_CODE: Final = "\033[0m"
COLOR_CODE_REGEX: Final = re.compile(r"\033\[[\d\;]+m")


@dataclass(frozen=True)
class Color:
    """
    Represents either a terminal color name or an RGB value,
    with ANSI escape code generation support.
    """

    terminal_color: Optional[str] = None
    rgb: Optional[Tuple[int, int, int]] = None

    def __post_init__(self):
        count = sum(x is not None for x in (self.terminal_color, self.rgb))
        if count > 1:
            raise ValueError("At most one of terminal_color or rgb can be set.")

    @classmethod
    def from_param(cls, color_data: Any) -> "Color":
        if isinstance(color_data, str):
            return cls.from_terminal(color_data)
        if isinstance(color_data, tuple):
            # TODO Make this more flexible
            r, g, b = color_data
            return cls.from_rgb(r, g, b)
        raise TypeError(f"Unsupported color type: {type(color_data)}")

    @classmethod
    def from_terminal(cls, color_name: str) -> "Color":
        color_name = str(color_name).strip().lower()
        if color_name not in ANSI_COLOR_CODES:
            raise ValueError(f"Invalid color str: '{color_name}'")
        return cls(terminal_color=color_name)

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> "Color":
        r = _clip_to_valid_int(r)
        g = _clip_to_valid_int(g)
        b = _clip_to_valid_int(b)
        return cls(rgb=(r, g, b))

    def is_enabled(self) -> bool:
        return self.terminal_color is not None or self.rgb is not None

    def colorize(self, string: str) -> str:
        if not self.is_enabled():
            return string
        return self.enable_str() + str(string) + COLOR_RESET_CODE

    def enable_str(self) -> str:
        if self.terminal_color:
            return ANSI_COLOR_CODES[self.terminal_color]
        r, g, b = self.rgb  # type: ignore
        # Template: '\033[38;2;146;255;12mHello!\033[0m'
        return f"\033[38;2;{r};{g};{b}m"


def _clip_to_valid_int(x, x_min=0, x_max=255):
    return max(min(int(x), x_max), x_min)
