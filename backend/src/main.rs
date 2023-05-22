use rocket::{catch, catchers, fs::NamedFile, get, routes, Request};
use rocket_okapi::swagger_ui::*;

use backend::ade::{Client, Credentials};

use std::path::{Path, PathBuf};

#[get("/")]
async fn index() -> Option<NamedFile> {
    println!("In index");
    NamedFile::open("../frontend/dist/index.html").await.ok()
}

#[get("/<file..>")]
async fn files(file: PathBuf) -> Option<NamedFile> {
    println!("In files {:?}", file);
    NamedFile::open(Path::new("../frontend/dist/").join(file))
        .await
        .ok()
}

#[catch(404)]
async fn catch_all(_req: &Request<'_>) -> Option<NamedFile> {
    NamedFile::open("../frontend/dist/index.html").await.ok()
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
        .register("/", catchers![catch_all])
        .manage(client)
        .mount("/", routes![index, files])
        .mount(
            "/api/",
            rocket_okapi::openapi_get_routes![
                backend::routes::calendar,
                backend::routes::classrooms
            ],
        )
        .mount(
            "/api/docs",
            make_swagger_ui(&SwaggerUIConfig {
                url: "../openapi.json".to_owned(),
                ..Default::default()
            }),
        )
        .launch()
        .await?;

    Ok(())
}
