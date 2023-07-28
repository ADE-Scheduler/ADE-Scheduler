//! Easily build requests to ADE's API.

use serde::Deserialize;

use super::{
    error::Result,
    xml::{Parameters, Projects, Resources},
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
}
