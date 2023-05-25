//! HTTP routes.

use rocket::{get, State};
use rocket_okapi::openapi;

use super::ade::Client;
use std::{thread, time};

#[openapi]
#[get("/calendar")]
pub fn calendar(_state: &State<Client>) -> &'static str {
    std::thread::sleep(time::Duration::from_secs(2));
    "You are on the calendar page!"
}

#[openapi]
#[get("/classrooms")]
pub fn classrooms(_state: &State<Client>) -> &'static str {
    "You are on the classrooms page!"
}
