use serde::Deserialize;

use super::error::Result;
use super::xml::Resources;

pub struct Credentials {
    pub url: String,
    pub data: String,
    pub authorization: String,
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
    pub async fn get_token(&self) -> Result<Token> {
        let response = self
            .client
            .get(&self.credentials.url)
            .header("Authorization", &self.credentials.authorization)
            .form(&self.credentials.data)
            .send()
            .await?;

        let token = response.json::<Token>().await?;

        Ok(token)
    }

    pub async fn get_resources(&self, token: Token, project_id: u32) -> Result<Resources> {
        let response = self
            .client
            .get(format!(
                "https://gw.api.uclouvain.be/ade/v0/projects/\
                {project_id}/function=getResources&tree=false&detail=13"
            ))
            .bearer_auth(token.access_token)
            .send()
            .await?;
        let resources = response.text().await?.parse()?;

        Ok(resources)
    }
}
