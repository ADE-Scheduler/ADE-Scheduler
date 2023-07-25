use rocket::{
    get,
    http::{Cookie, CookieJar, SameSite},
    response::Redirect,
};
use rocket_oauth2::{OAuth2, TokenResponse};

pub struct UCLouvain;

// This route calls `get_redirect`, which sets up a token request and
// returns a `Redirect` to the authorization endpoint.
#[get("/login/uclouvain")]
pub fn uclouvain_login(oauth2: OAuth2<UCLouvain>, cookies: &CookieJar<'_>) -> Redirect {
    // We want the "user:read" scope. For some providers, scopes may be
    // pre-selected or restricted during application registration. We could
    // use `&[]` instead to not request any scopes, but usually scopes
    // should be requested during registation, in the redirect, or both.
    oauth2.get_redirect(cookies, &[]).unwrap()
}

// This route, mounted at the application's Redirect URI, uses the
// `TokenResponse` request guard to complete the token exchange and obtain
// the token.
#[get("/login")]
pub fn uclouvain_callback(token: TokenResponse<UCLouvain>, cookies: &CookieJar<'_>) -> Redirect {
    // Set a private cookie with the access token
    cookies.add_private(
        Cookie::build("token", token.access_token().to_string())
            .same_site(SameSite::Lax)
            .finish(),
    );
    Redirect::to("/")
}
