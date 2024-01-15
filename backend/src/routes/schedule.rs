/// Schedule routes.

use std::collections::HashMap;

use rocket::serde::json::Json;
use rocket::{get, post, delete, patch, State};
use rocket_okapi::openapi;

use crate::{
    core::{Schedule,Event},
    error::Result,
};

/// Returns all the events from the current schedule,
/// grouped by code.
#[openapi]
#[get("/schedule/events")]
pub async fn get_events(
) -> Result<Json<HashMap<String, Vec<String>>>> {

    todo!()
}

/// Adds a code to the current schedule and returns the associated events.
#[openapi]
#[post("/schedule/events/<code>")]
pub async fn add_code(
    code: &str,
) -> Result<Json<String>> {
    let s = format!("Post code {code}");

    Ok(Json(s))
}

/// Deletes a code from the current schedule.
#[openapi]
#[delete("/schedule/schedule/events/<code>")]
pub async fn delete_code(
    code: &str,
) -> Result<Json<String>> {
    let s = format!("Delete code {code}");

    Ok(Json(s))
}

/// Returns the events associated to the given code.
#[openapi]
#[patch("/schedule/events/<code>")]
pub async fn patch_code(
    code: &str,
) -> Result<Json<String>> {
    let s = format!("Get code {code}");

    Ok(Json(s))
}
