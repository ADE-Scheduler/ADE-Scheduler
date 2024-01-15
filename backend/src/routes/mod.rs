//! HTTP routes.

use rocket::{get, State};
use rocket_okapi::openapi;

pub mod calendar;
pub mod oauth;
pub mod schedule;

pub use oauth::*;

#[openapi]
#[get("/classrooms")]
pub fn classrooms() -> &'static str {
    "You are on the classrooms page!"
}
