use rocket::{catch, catchers, fs::NamedFile, get, routes, Request};
use rocket_okapi::swagger_ui::*;

use backend::{
    ade::{Client, Credentials},
    error::Result,
};

use std::path::{Path, PathBuf};

#[get("/")]
async fn index() -> Option<NamedFile> {
    NamedFile::open("../frontend/dist/index.html").await.ok()
}

#[get("/<file..>")]
async fn files(file: PathBuf) -> Option<NamedFile> {
    log::info!("Loading file {:?} from dist/ folder...", file);
    NamedFile::open(Path::new("../frontend/dist/").join(file))
        .await
        .ok()
}

#[catch(404)]
async fn catch_all(req: &Request<'_>) -> Option<NamedFile> {
    log::info!(
        "Catch all: uri {} not found, falling back to index.html.",
        req.uri()
    );
    NamedFile::open("../frontend/dist/index.html").await.ok()
}

fn rocket() -> Result<rocket::Rocket<rocket::Build>> {
    // Loading environ variables from .env file
    dotenv::dotenv().ok();

    let rocket = rocket::build();
    let figment = rocket.figment();

    log::info!("Reading ADE credentials from config file...");
    let credentials: Credentials = figment
        .extract_inner("ade")
        .expect("ade credentials should be present in the config file");

    log::info!("Creating ADE  client with credentials...");
    let ade_client = Client::new(credentials);

    let redis_client: redis::Client = redis::Client::open(
        figment
            .find_value("redis.url")
            .expect("redis.url should be present in the config file")
            .as_str()
            .expect("redis.url should be a string"),
    )?;

    let redis_connection = redis_client.get_connection()?;

    let rocket = rocket
        .register("/", catchers![catch_all])
        .manage(ade_client)
        .manage(redis_connection)
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
        );

    Ok(rocket)
}

#[rocket::main]
async fn main() -> Result<()> {
    let _ = rocket()?.launch().await?;

    Ok(())
}

#[cfg(test)]
mod test {
    use super::rocket;
    use rocket::{http::Status, local::blocking::Client, uri, State};

    #[test]
    fn docs_route() {
        let client = Client::tracked(rocket().unwrap()).expect("valid rocket instance");
        let response = client.get("/api/docs").dispatch();
        assert_eq!(response.status(), Status::SeeOther);
        let response = client.get("/api/docs/index.html").dispatch();
        assert_eq!(response.status(), Status::Ok);
    }

    #[rocket::async_test]
    async fn client_state() {
        let rocket = rocket().unwrap();
        let client: &State<backend::ade::Client> =
            State::get(&rocket).expect("rocket should manage a backend::ade::Client instance");
        let token = client.get_token().await;
        assert!(token.is_ok());
    }
}
