#[rocket::get("/calendar")]
pub fn calendar() -> &'static str {
    "You are on the calendar page!"
}

#[rocket::get("/classrooms")]
pub fn classrooms() -> &'static str {
    "You are on the classrooms page!"
}
