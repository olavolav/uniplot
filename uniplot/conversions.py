import numpy as np
import datetime
from typing import Any, Final

COLOR_CODES: Final = {
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "red": "\033[31m",
}


def floatify(x: Any) -> float:
    """
    Convert anything to a float, including integers and time stamps.

    Implementation note: It is really important that throughout the library we
    use the "datetime64[s]" NumPy format consistently. Using only `np.datetime`
    or a different type like "datetime64[m]" means that the conversion to
    floating point will depend on the input format, which will lead to
    unexpected behavior.
    """
    try:
        if np.issubdtype(x.dtype, np.datetime64):
            return x.astype("datetime64[s]").astype(float)
        return float(x)
    except AttributeError:
        if isinstance(x, datetime.datetime) or isinstance(x, datetime.date):
            return np.datetime64(x).astype("datetime64[s]").astype(float)
        return float(x)
