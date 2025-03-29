import datetime
from typing import Any, Final
import numpy as np
from numpy.typing import NDArray


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


def convert_matrix_to_rows_of_submatrices(
    matrix: NDArray, width_submatrix: int, height_submatrix: int
) -> NDArray:
    """
    This returns a list of submatrices.

    Example:
    > x = np.array([[0, 1, 2, 3],
                    [0, 4, 5, 6],
                    [1, 7, 8, 9],
                    [2, 8, 9, 0]])
    > convert_matrix_to_rows_of_submatices(x, 2, 2)
      array([[[0, 1, 0, 4],
              [2, 3, 5, 6]],
             [[1, 7, 2, 8],
              [8, 9, 9, 0]]])
    """
    assert width_submatrix > 0
    assert height_submatrix > 0
    assert matrix.shape[0] % height_submatrix == 0
    assert matrix.shape[1] % width_submatrix == 0

    (height, width) = matrix.shape

    # Reshape into submatrices of shape (num_rows, num_cols, height_submatrix, width_submatrix)
    submatrices = matrix.reshape(
        height // height_submatrix,
        height_submatrix,
        width // width_submatrix,
        width_submatrix,
    )

    # Transpose axes to bring the submatrix blocks into the correct order
    submatrices = submatrices.transpose(0, 2, 1, 3)

    # Reshape to flatten each submatrix into a row
    flattened_submatrices = submatrices.reshape(
        height // height_submatrix, width // width_submatrix, -1
    )

    return flattened_submatrices
