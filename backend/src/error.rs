//! Error and Result structures used all across this crate.
use std::io::Cursor;

use rocket::{
    http::{ContentType, Status},
    request::Request,
    response::{self, Responder, Response},
};

/// Enumeration of all possible error types.
#[derive(Debug, thiserror::Error)]
pub enum Error {
    /// Error with database (see [`diesel::result::Error`]).
    #[error(transparent)]
    DatabaseError(#[from] diesel::result::Error),

    /// Error with HTTP request (see [`reqwest::Error`]).
    #[error(transparent)]
    HttpRequest(#[from] reqwest::Error),

    /// Error that occurs if a UCLouvainId is invalid (see
    /// [`backend::models::UCLouvainID`]).
    #[error("Invalid UCLouvainID: {0}")]
    InvalidUCLouvainID(String),

    /// Error with Redis (see [`redis::RedisError`]).
    #[error(transparent)]
    Redis(#[from] redis::RedisError),

    /// Error with Rocket (see [`rocket::Error`]).
    #[error(transparent)]
    Rocket(#[from] rocket::Error),

    /// Error that occurs if a UCLouvain a not known role (see
    /// [`backend::json::BusinessRoleCode`]).
    #[error("This user has no employee or student role at UCLouvain, this is not normal!")]
    UserHasNoKnownRole,

    /// Error during XML deserialization (see [`quick_xml::de::DeError`]).
    #[error(transparent)]
    XmlDeserialization(#[from] quick_xml::de::DeError),
}

/// Result type alias with error type defined above (see [`Error`]).
pub type Result<T> = std::result::Result<T, Error>;

impl<'r> Responder<'r, 'static> for Error {
    fn respond_to(self, _: &'r Request<'_>) -> response::Result<'static> {
        let message = format!("InternalServerError: {self}");
        Response::build()
            .header(ContentType::Plain)
            .status(Status::InternalServerError)
            .sized_body(message.len(), Cursor::new(message))
            .ok()
    }
}
