use rocket::serde::json::Json;
/// Calendar routes.
use rocket::{get, State};
use rocket_okapi::openapi;

use crate::{ade, error::Result, xml::Activities};

/// Returns the [`Activities`] for a given code. The case is ignored.
///
/// If the code does not exist, no event will be returned.
/// TODO: an appriopriate error code must be returned.
/// TODO: use Redis for storing intermediate requests.
/// TODO: use Redis pool
#[openapi]
#[get("/calendar/<code>")]
pub async fn calendar(
    code: &str,
    ade_client: &State<ade::Client>,
    token: ade::Token,
) -> Result<Json<Activities>> {
    println!("Some token {token:?}");
    let project = ade_client
        .get_projects(&token)
        .await
        .expect("project should be valid")[0]
        .clone();

    let resources = ade_client.get_resources(&token, project.id).await;

    // TODO: handle errors better
    assert!(resources.is_ok());

    let resources = resources.unwrap();

    let code = code.to_uppercase();

    let activity_ids = resources.iter().filter_map(|resource| {
        if resource.name.to_uppercase().eq(&code) {
            Some(resource.id)
        } else {
            None
        }
    });

    let activities = ade_client
        .get_activities(&token, project.id, activity_ids)
        .await?;
    Ok(Json(activities))
}
