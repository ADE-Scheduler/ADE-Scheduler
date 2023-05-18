use backend::ade::{Client, Credentials};

#[rocket::get("/")]
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

    rocket
        .mount(
            "/",
            rocket::routes![
                index,
                backend::routes::calendar,
                backend::routes::classrooms
            ],
        )
        .launch()
        .await?;

    Ok(())
}
