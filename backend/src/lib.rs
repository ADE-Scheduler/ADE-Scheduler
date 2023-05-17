use pyo3::prelude::*;

pub mod xml;

/*
struct Activity {
    id: usize,
    name: String,
    _type: String,
    events: Vec<Event>,
}

struct Event {
    id: usize,
    name: String,
    end_hour: Date,
    start_hour: Date,
    date: Date,
    info: String,
    note: String,
    event_participants: Vec<EventParticipant>,
}

struct EventParticipant {
    category: Category,
    name: String,
}

enum Category {
    Trainee,
    Instructor,
    Classroom,
    Equipment,
    Category5,
    Category6,
    Category7,
    Category8,
}

fn parse_activity(doc: Document<'_>) -> Result<Activity, String> {

}
*/

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn backend(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}
