use rocket::{catch, catchers, fs::NamedFile, get, routes, Request};
use rocket_db_pools::{
    diesel::{prelude::*, PgPool},
    Connection, Database,
};
use rocket_okapi::swagger_ui::*;
use std::env;

use backend::{ade, error::Result, models::User, my};

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

#[derive(Database)]
#[database("ade-database")]
struct Db(PgPool);

#[get("/users")]
async fn list_users(mut db: Connection<Db>) -> String {
    let results = backend::schema::users::dsl::users
        .load::<User>(&mut *db)
        .await
        .expect("Failed to query users");

    format!("{results:#?}")
}

/*
#[get("/user/<id>/<name>")]
async fn create_user(mut db: Connection<Db>, id: i32, name: String) -> String {
    let user = User { id, name };
    diesel::insert_into(backend::schema::users::dsl::users)
        .values(&user)
        .execute(&mut *db)
        .await
        .expect("Error creating user");

    format!("{:#?}", "ok")
}*/

fn rocket() -> Result<rocket::Rocket<rocket::Build>> {
    // Loading environ variables from .env file
    dotenvy::dotenv().ok();

    let rocket = rocket::build();
    let figment = rocket.figment();

    log::info!("Reading ADE credentials from config file...");
    let ade_credentials: ade::Credentials = figment
        .extract_inner("ade")
        .expect("ADE credentials should be present in the config file");

    log::info!("Creating ADEclient with credentials...");
    let ade_client = ade::Client::new(ade_credentials);

    log::info!("Reading My credentials from config file...");
    let my_credentials: my::Credentials = figment
        .extract_inner("my")
        .expect("My credentials should be present in the config file");

    log::info!("Creating My client with credentials...");
    let my_client = my::Client::new(my_credentials);

    let redis_client: redis::Client = redis::Client::open(
        figment
            .find_value("redis.url")
            .expect("redis.url should be present in the config file")
            .as_str()
            .expect("redis.url should be a string"),
    )?;

    let rocket = rocket
        .register("/", catchers![catch_all])
        .manage(ade_client)
        .manage(my_client)
        .manage(redis_client)
        .mount(
            "/",
            routes![
                index,
                files,
                list_users,
                backend::routes::uclouvain_callback,
                backend::routes::uclouvain_login
            ],
        )
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
        .attach(rocket_oauth2::OAuth2::<backend::routes::UCLouvain>::fairing("uclouvain"))
        .attach(Db::init());

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
    use rocket::{http::Status, local::blocking::Client, tokio::runtime::Runtime, State};

    lazy_static::lazy_static! {
        static ref ROCKET: rocket::Rocket<rocket::Build> = rocket().unwrap();
        static ref ADE_CLIENT: &'static State<backend::ade::Client> =
            State::get(&ROCKET).unwrap();
        static ref TOKEN: backend::ade::Token = Runtime::new().unwrap().block_on(async {ADE_CLIENT.get_token().await.unwrap()});
    }

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

    #[rocket::async_test]
    async fn client_get_projects() {
        use chrono::Datelike;

        let projects = ADE_CLIENT.get_projects(&TOKEN).await;

        assert!(projects.is_ok());

        let projects = projects.unwrap();

        let this_year = chrono::Utc::now().year().to_string();

        assert!(!projects.is_empty());

        for project in projects.iter() {
            assert!(project.name.contains(&this_year));
        }
    }

    #[rocket::async_test]
    async fn client_get_resources() {
        let rocket = rocket().unwrap();
        let client: &State<backend::ade::Client> =
            State::get(&rocket).expect("rocket should manage a backend::ade::Client instance");
        let token = client.get_token().await.expect("token should be valid");
        let project = client
            .get_projects(&token)
            .await
            .expect("project should be valid")[0]
            .clone();

        let resources = client.get_resources(&token, project.id).await;

        assert!(resources.is_ok());

        let resources = resources.unwrap();

        assert!(matches!(
            resources
                .iter()
                .find(|resource| { resource.name.to_uppercase().starts_with("LEPL1101") }),
            Some(_)
        ));
    }

    #[test]
    fn redis_connection_state() {
        let rocket = rocket().unwrap();
        let client: &State<redis::Client> =
            State::get(&rocket).expect("rocket should manage a redis::Client instance");
        let mut con = client
            .get_connection()
            .expect("failed to connect to the redis server");
        let ping: redis::RedisResult<String> = redis::cmd("PING").query(&mut con);

        assert!(ping.is_ok());
        assert_eq!(ping.unwrap(), "PONG");
    }

    /*
    #[test]
    fn redis_set_resources_hashmap() {
        let rocket = rocket().unwrap();
        let ade_client: &State<backend::ade::Client> =
            State::get(&rocket).expect("rocket should manage a backend::ade::Client instance");
        let token =ade_client.get_token().await.expect("token should be valid");
        let project = ade_client
            .get_projects(&token)
            .await
            .expect("project should be valid")[0]
            .clone();

        let resources = client.get_resources(&token, project.id).await;

        assert!(resources.is_ok());

        let resources = resources.unwrap();

        assert!(matches!(
            resources
                .iter()
                .find(|resource| { resource.name.to_uppercase().starts_with("LEPL1101") }),
            Some(_)
        ));
        let rocket = rocket().unwrap();
        let client: &State<redis::Client> =
            State::get(&rocket).expect("rocket should manage a redis::Client instance");
        let mut con = client
            .get_connection()
            .expect("failed to connect to the redis server");
        let ping: redis::RedisResult<String> = redis::cmd("PING").query(&mut con);

        assert!(ping.is_ok());
        assert_eq!(ping.unwrap(), "PONG");
    }*/
}
