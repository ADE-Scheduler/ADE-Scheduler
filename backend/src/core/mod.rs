//! Core backend logic.

use std::collections::HashMap;

pub struct Schedule {
    pub id: u32,
    pub project_id: u32,
    pub name: String,
    pub codes: Vec<String>,
    pub filters: HashMap<String, Vec<String>>,
}

pub struct Event {

}
