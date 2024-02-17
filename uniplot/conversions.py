import numpy as np
from typing import Any


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
    except:
        return float(x)
