use rocket::get;
use rocket_okapi::{openapi, swagger_ui::*};

use backend::ade::{Client, Credentials};

/// Index page.
#[openapi]
#[get("/")]
fn index() -> &'static str {
    "Hello, world!"
}

#[rocket::main]
async fn main() -> Result<(), rocket::Error> {
    // Loading environ variables from .env file
    dotenv::dotenv().ok();

    let rocket = rocket::build();
    let figment = rocket.figment();

    let credentials: Credentials = figment.extract_inner("ade").expect("ade");

    println!("credentials: {credentials:#?}");

    let client = Client::new(credentials);

    let token = client.get_token().await.unwrap();
    println!("Token: {token:?}");

    let _ = rocket
        .mount(
            "/",
            rocket_okapi::openapi_get_routes![
                index,
                backend::routes::calendar,
                backend::routes::classrooms
            ],
        )
        .mount(
            "/swagger-ui/",
            make_swagger_ui(&SwaggerUIConfig {
                url: "../openapi.json".to_owned(),
                ..Default::default()
            }),
        )
        .launch()
        .await?;

    Ok(())
}
