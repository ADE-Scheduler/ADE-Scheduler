//! Easily build requests to UCLouvain's My API.

use serde::Deserialize;

use super::{
    error::Result,
    json::{BusinessRoles, Employee, Student},
};

#[derive(Debug, Deserialize)]
pub struct Credentials {
    pub url: String,
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

    pub async fn get_roles(&self, access_token: &str) -> Result<BusinessRoles> {
        let url = &self.credentials.url;
        let response = self
            .client
            .get(format!("{url}/digit/roles"))
            .bearer_auth(access_token)
            .send()
            .await?;

        let roles = response.json().await?;

        Ok(roles)
    }

    pub async fn get_employee(&self, access_token: &str) -> Result<Employee> {
        let url = &self.credentials.url;
        let response = self
            .client
            .get(format!("{url}/employee"))
            .bearer_auth(access_token)
            .send()
            .await?;

        let employee = response.json().await?;

        Ok(employee)
    }

    pub async fn get_student(&self, access_token: &str) -> Result<Student> {
        let url = &self.credentials.url;
        let response = self
            .client
            .get(format!("{url}/student"))
            .bearer_auth(access_token)
            .send()
            .await?;

        let student = response.json().await?;

        Ok(student)
    }
}
