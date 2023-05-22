//! HTTP routes.

use rocket::{get, State};
use rocket_okapi::openapi;

use super::ade::Client;

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
