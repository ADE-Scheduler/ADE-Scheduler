#[rocket::get("/")]
fn index() -> &'static str {
    "Hello, world!"
}

#[rocket::launch]
fn rocket() -> _ {
    rocket::build().mount(
        "/",
        rocket::routes![
            index,
            backend::routes::calendar,
            backend::routes::classrooms
        ],
    )
}
