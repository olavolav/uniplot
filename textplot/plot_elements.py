import numpy as np  # type: ignore

UNICODE_SQUARES = {
    0: " ",
    1: "▘",
    2: "▝",
    3: "▀",
    4: "▖",
    5: "▌",
    6: "▞",
    7: "▛",
    8: "▗",
    9: "▚",
    10: "▐",
    11: "▜",
    12: "▄",
    13: "▙",
    14: "▟",
    15: "█",
}
BINARY_ENCODING_MATRIX = np.array([[1, 2], [4, 8]])


def character_for_2by2_pixels(square: np.array) -> str:
    """
    Convert 2x2 matrix to unicode character representation for plotting.
    """
    # Convert matric to integer
    # NOTE That this will fail if the square is not 2x2 or contains anything else than
    # zeros and ones
    integer_encoding = np.multiply(square, BINARY_ENCODING_MATRIX).sum()
    return UNICODE_SQUARES[integer_encoding]
