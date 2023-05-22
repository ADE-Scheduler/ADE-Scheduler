//! Error and Result structures used all across this crate.

/// Enumeration of all possible error types.
#[derive(Debug, thiserror::Error)]
pub enum Error {
    /// Error with HTTP request (see [`reqwest::Error`]).
    #[error(transparent)]
    HttpRequest(#[from] reqwest::Error),

    /// Error with Redis (see [`redis::RedisError`]).
    #[error(transparent)]
    Redis(#[from] redis::RedisError),

    /// Error with Rocket (see [`rocket::Error`]).
    #[error(transparent)]
    Rocket(#[from] rocket::Error),

    /// Error during XML deserialization (see [`quick_xml::de::DeError`]).
    #[error(transparent)]
    XmlDeserialization(#[from] quick_xml::de::DeError),
}

/// Result type alias with error type defined above (see [`Error`]).
pub type Result<T> = std::result::Result<T, Error>;
