//! Easily build requests to ADE's API.

use rocket::{
    http::Status,
    request::{FromRequest, Outcome, Request},
};
use rocket_okapi::{
    gen::OpenApiGenerator,
    request::{OpenApiFromRequest, RequestHeaderInput},
};
use serde::Deserialize;

use super::{
    error::{Error, Result},
    redis::{Connection, Redis},
    xml::{Activities, Parameters, Projects, Resources},
};

#[derive(Debug, Deserialize)]
pub struct Endpoints {
    pub api: String,
    pub token: String,
}

#[derive(Debug, Deserialize)]
pub struct Credentials {
    pub url: String,
    pub data: String,
    pub authorization: String,
    pub endpoints: Endpoints,
}

pub struct Client {
    pub client: reqwest::Client,
    pub credentials: Credentials,
}

#[derive(Debug, Deserialize)]
pub struct Token {
    pub access_token: String,
    pub expires_in: u32,
}

impl<'r> OpenApiFromRequest<'r> for Token {
    fn from_request_input(
        _gen: &mut OpenApiGenerator,
        _name: String,
        _required: bool,
    ) -> rocket_okapi::Result<RequestHeaderInput> {
        Ok(RequestHeaderInput::None)
    }
}

#[rocket::async_trait]
impl<'r> FromRequest<'r> for Token {
    type Error = Option<&'static str>;

    async fn from_request(req: &'r Request<'_>) -> Outcome<Self, Self::Error> {
        match req.guard::<Connection<Redis>>().await {
            Outcome::Success(mut con) => {
                let token = match redis::pipe()
                    .cmd("GET")
                    .arg("ade-token")
                    .cmd("TTL")
                    .arg("ade-token")
                    .query_async(&mut *con)
                    .await
                {
                    Ok((access_token, expires_in)) => {
                        Token {
                            access_token,
                            expires_in,
                        }
                    },
                    _ => {
                        match req.rocket().state::<Client>() {
                            Some(ade_client) => {
                                match ade_client.get_token().await {
                                    Ok(token) => {
                                        let _result: redis::RedisResult<String> =
                                            redis::Cmd::set_ex(
                                                "ade-token",
                                                &token.access_token,
                                                token.expires_in as usize,
                                            )
                                            .query_async(&mut *con)
                                            .await;
                                        token
                                    },
                                    Err(_) => {
                                        return Outcome::Failure((
                                            Status::InternalServerError,
                                            None,
                                        ));
                                    },
                                }
                            },
                            None => return Outcome::Failure((Status::InternalServerError, None)),
                        }
                    },
                };
                Outcome::Success(token)
            },
            _ => Outcome::Failure((Status::InternalServerError, None)),
        }
    }
}

impl Client {
    pub fn new(credentials: Credentials) -> Self {
        Self {
            client: reqwest::Client::new(),
            credentials,
        }
    }
    pub async fn get_token(&self) -> Result<Token> {
        let url = &self.credentials.url;
        let token = &self.credentials.endpoints.token;
        let response = self
            .client
            .post(format!("{url}/{token}",))
            .header("Authorization", &self.credentials.authorization)
            .body(self.credentials.data.clone())
            .send()
            .await?;

        let token = response.json::<Token>().await?;

        Ok(token)
    }

    pub async fn get_projects(&self, token: &Token) -> Result<Projects> {
        let url = &self.credentials.url;
        let api = &self.credentials.endpoints.api;
        let response = self
            .client
            .get(format!("{url}/{api}/projects"))
            .query(Projects::parameters())
            .bearer_auth(token.access_token.clone())
            .send()
            .await?;

        let resources = response.text().await?.parse()?;

        Ok(resources)
    }

    pub async fn get_resources(&self, token: &Token, project_id: u32) -> Result<Resources> {
        let url = &self.credentials.url;
        let api = &self.credentials.endpoints.api;
        let response = self
            .client
            .get(format!("{url}/{api}/projects/{project_id}/resources"))
            .query(Resources::parameters())
            .bearer_auth(token.access_token.clone())
            .send()
            .await?;

        let resources = response.text().await?.parse()?;

        Ok(resources)
    }

    pub async fn get_activities<I>(
        &self,
        token: &Token,
        project_id: u32,
        activity_ids: I,
    ) -> Result<Activities>
    where
        I: Iterator<Item = u32>,
    {
        let url = &self.credentials.url;
        let api = &self.credentials.endpoints.api;
        let mut ids = String::new();

        for id in activity_ids {
            ids.push_str(&id.to_string());
            ids.push('|');
        }
        ids.pop();

        let response = self
            .client
            .get(format!("{url}/{api}/projects/{project_id}/activities"))
            .query(Activities::parameters())
            .query(&[("resources", ids)])
            .bearer_auth(token.access_token.clone())
            .send()
            .await?;

        let activities = response.text().await?.parse()?;

        Ok(activities)
    }
}
