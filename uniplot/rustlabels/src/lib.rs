use pyo3::prelude::*;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn float_axis_labels(x_min: f64, x_max: f64, available_space: u32, vertical_direction: bool, unit: String) -> PyResult<String> {
    let labels = axis_labels_rs::float_axis_labels(x_min, x_max, available_space, 1, vertical_direction, &unit);
    return Ok(labels);
}

/// A Python module implemented in Rust.
#[pymodule]
fn rustlabels(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(float_axis_labels, m)?)?;
    Ok(())
}
