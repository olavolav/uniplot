import numpy as np  # type: ignore


def restricted_heckbert_ticks(x_min: float, x_max: float, nr_ticks: int) -> np.array:
    best_ticks = None
    for _ in range(2, 10):
        raw_ticks = heckbert_ticks(x_min=x_min, x_max=x_max, nr_ticks=nr_ticks)
        filtered_ticks = raw_ticks[(raw_ticks >= x_min) & (raw_ticks <= x_max)]
        if best_ticks is None or (
            abs(len(best_ticks) - nr_ticks) > abs(len(filtered_ticks) - nr_ticks)
        ):
            best_ticks = filtered_ticks
    return best_ticks


def heckbert_ticks(x_min: float, x_max: float, nr_ticks: int) -> np.array:
    data_range = x_max - x_min

    # Step 1: Find a temporary range that is a power of ten of 1, 2, or 5 which covers the size of the actual range
    exponent = np.int(np.log10(data_range))
    fraction_part = data_range / (10 ** exponent)
    new_fraction_part = 10
    if fraction_part <= 1:
        new_fraction_part = 1
    elif fraction_part <= 2:
        new_fraction_part = 2
    elif fraction_part <= 5:
        new_fraction_part = 5
    intermediate_range = new_fraction_part * (10 ** exponent)

    # Step 2: Using the temporary range `intermediate_range`, we use the desired number of tick marks to divide it into small segments. This number gets compared against key cutoff values of 1.5, 3, and 7 to determine the step increment.
    # Note that, the pieces of code using `np.int`, `log10` and `10**` are adjusting for magnitude. That is, if the temporary range was 20, 200, or 2000, the step increment will become 2, 20, or 200 respectively.
    intermediate_tick_step = intermediate_range / (nr_ticks - 1)

    tick_exponent = np.int(np.log10(intermediate_tick_step))

    tick_fraction_part = intermediate_tick_step / (10 ** tick_exponent)

    new_tick_fraction_part = 10
    if tick_fraction_part < 1.5:
        new_tick_fraction_part = 1
    elif tick_fraction_part < 3:
        new_tick_fraction_part = 2
    elif tick_fraction_part < 7:
        new_tick_fraction_part = 5

    nice_tick_increment = new_tick_fraction_part * (10 ** tick_exponent)

    # Step 3: We use the tick mark increment to derive nice minimum and nice maximum. Using the `np.int` and `ceil` functions ensures the minimum and maximum, respectively, are in stride with the nice tick mark increment.
    nice_min = np.int(x_min / nice_tick_increment) * nice_tick_increment
    nice_max = np.ceil(x_max / nice_tick_increment) * nice_tick_increment

    return np.arange(
        nice_min, nice_max + 0.5 * nice_tick_increment, step=nice_tick_increment
    )
