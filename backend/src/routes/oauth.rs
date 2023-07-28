use rocket::{
    get,
    http::{Cookie, CookieJar, SameSite},
    response::Redirect,
    State,
};
use rocket_oauth2::{OAuth2, TokenResponse};

use crate::{
    error::{Error, Result},
    my,
};

pub struct UCLouvain;

// This route calls `get_redirect`, which sets up a token request and
// returns a `Redirect` to the authorization endpoint.
#[get("/login/uclouvain")]
pub fn uclouvain_login(oauth2: OAuth2<UCLouvain>, cookies: &CookieJar<'_>) -> Redirect {
    oauth2.get_redirect(cookies, &["user:read"]).unwrap()
}

// This route, mounted at the application's Redirect URI, uses the
// `TokenResponse` request guard to complete the token exchange and obtain
// the token.
#[get("/login")]
pub async fn uclouvain_callback(
    token: TokenResponse<UCLouvain>,
    cookies: &CookieJar<'_>,
    client: &State<my::Client>,
) -> Result<Redirect> {
    use crate::json::BusinessRoleCode::*;
    // Set a private cookie with the access token
    println!("token: {}", token.access_token().to_string());
    cookies.add_private(
        Cookie::build("token", token.access_token().to_string())
            .same_site(SameSite::Lax)
            .finish(),
    );
    let roles = client.get_roles(token.access_token()).await?;

    let role = roles.first_role().ok_or(Error::UserHasNoKnownRole)?;

    match role.business_role_code {
        Employee => {
            let employee = client.get_employee(token.access_token()).await?;
            println!("employee: {employee:?}")
        },
        Student => {
            let student = client.get_student(token.access_token()).await?;
            println!("student: {student:?}")
        },
        Unknown => return Err(Error::UserHasNoKnownRole),
    }
    println!("roles: {:?}", roles);

    Ok(Redirect::to("/"))
}
