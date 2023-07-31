//! HTTP routes.

use rocket::{get, State};
use rocket_okapi::openapi;

use super::ade::Client;

pub mod calendar;
pub mod oauth;

pub use oauth::*;

#[openapi]
#[get("/classrooms")]
pub fn classrooms(_state: &State<Client>) -> &'static str {
    "You are on the classrooms page!"
}
