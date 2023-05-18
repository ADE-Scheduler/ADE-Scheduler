use rocket::get;
use rocket_okapi::openapi;

#[openapi]
#[get("/calendar")]
pub fn calendar() -> &'static str {
    "You are on the calendar page!"
}

#[openapi]
#[get("/classrooms")]
pub fn classrooms() -> &'static str {
    "You are on the classrooms page!"
}
