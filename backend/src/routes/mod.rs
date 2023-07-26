//! HTTP routes.
pub mod oauth;

use rocket::{get, State};
use rocket_okapi::openapi;

use super::ade::Client;

pub use oauth::*;

#[openapi]
#[get("/calendar")]
pub fn calendar(_state: &State<Client>) -> &'static str {
    "You are on the calendar page!"
}

#[openapi]
#[get("/classrooms")]
pub fn classrooms(_state: &State<Client>) -> &'static str {
    "You are on the classrooms page!"
}
