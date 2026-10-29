import datetime
from datetime import tzinfo
from typing import Any

import numpy as np
from numpy.typing import NDArray


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
        if isinstance(x, (datetime.datetime, datetime.date)):
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


def utc_to_local(dts: NDArray, timezone: tzinfo) -> NDArray:
    """
    Convert UTC timestamps to the local time in the timezone, both without a
    timezone.
    """
    return np.array(
        [
            datetime.datetime.fromtimestamp(t, timezone).replace(tzinfo=None)
            for t in dts.astype("datetime64[s]").astype(int)
        ],
        dtype="datetime64[s]",
    )


def local_to_utc(dts: NDArray, timezone: tzinfo) -> NDArray:
    """
    Convert local times in the timezone to sorted UTC timestamps, both without a
    timezone. A local time which occurs twice gives both, and a local time which
    is skipped gives none.
    """
    utc = []
    for t in dts.astype("datetime64[s]").astype(datetime.datetime):
        for fold in (0, 1):
            utc_time = t.replace(tzinfo=timezone, fold=fold).astimezone(
                datetime.timezone.utc
            )
            # A skipped local time does not survive the way back
            if utc_time.astimezone(timezone).replace(tzinfo=None) == t:
                utc.append(utc_time.replace(tzinfo=None))
    return np.unique(np.array(utc, dtype="datetime64[s]"))
