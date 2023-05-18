use rocket::serde::Deserialize;

use super::{error::Result, xml::Resources};

#[derive(Debug, Deserialize)]
#[serde(crate = "rocket::serde")]
pub struct Endpoints {
    pub api: String,
    pub token: String,
}

#[derive(Debug, Deserialize)]
#[serde(crate = "rocket::serde")]
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

impl Client {
    pub fn new(credentials: Credentials) -> Self {
        Self {
            client: reqwest::Client::new(),
            credentials,
        }
    }
    pub async fn get_token(&self) -> Result<Token> {
        let response = self
            .client
            .post(format!(
                "{}{}",
                self.credentials.url, self.credentials.endpoints.token
            ))
            .header("Authorization", &self.credentials.authorization)
            .body(self.credentials.data.clone())
            .send()
            .await?;

        let token = response.json::<Token>().await?;

        Ok(token)
    }

    pub async fn get_resources(&self, token: Token, project_id: u32) -> Result<Resources> {
        let url = &self.credentials.url;
        let api = &self.credentials.endpoints.api;
        let response = self
            .client
            .get(format!(
                "{url}{api}projects/{project_id}/function=getResources&tree=false&detail=13"
            ))
            .bearer_auth(token.access_token)
            .send()
            .await?;
        let resources = response.text().await?.parse()?;

        Ok(resources)
    }
}
