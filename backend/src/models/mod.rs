//! Database models.

use super::schema::users;
use diesel::prelude::*;
use serde::{
    de::{self, Deserializer, Visitor},
    Deserialize, Serialize,
};
use std::fmt;

/// UCLouvainID unique identifier for UCLouvain members,
/// and can be aliased as FGS, NOMA, etc.
///
/// UCLouvainID is usually an 8-digits string, which can contain leading zeros.
/// `UCLouvainID::to_string` solve this problem by appending leading zeros if
/// needed, but uses one `u32` for storage, which is far better than a string.
///
/// ```rust
/// # use backend::models::UCLouvainID;
/// let fgs = UCLouvainID(12345678);
/// assert_eq!("12345678", fgs.to_string());
///
/// // Accepts leading zeros;
/// let fgs = UCLouvainID(00123456);
/// assert_eq!("00123456", fgs.to_string());
#[derive(Clone, Debug)]
pub struct UCLouvainID(pub u32);

pub type FGS = UCLouvainID;
pub type NOMA = UCLouvainID;

impl fmt::Display for UCLouvainID {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:08}", self.0)
    }
}

impl std::ops::Deref for UCLouvainID {
    type Target = u32;
    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl std::ops::DerefMut for UCLouvainID {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0
    }
}

struct UCLouvainIDVisitor;

impl<'de> Visitor<'de> for UCLouvainIDVisitor {
    type Value = u32;
    // TODO: actually forbid values above 99_999_999

    fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
        formatter.write_str("an unsigned integer between 0 and 99_999_999 included")
    }

    fn visit_u64<E>(self, value: u64) -> Result<Self::Value, E>
    where
        E: de::Error,
    {
        value.try_into().map_err(de::Error::custom)
    }

    fn visit_str<E>(self, value: &str) -> Result<Self::Value, E>
    where
        E: de::Error,
    {
        value.parse().map_err(de::Error::custom)
    }
}

impl<'de> Deserialize<'de> for UCLouvainID {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        deserializer
            .deserialize_any(UCLouvainIDVisitor)
            .map(UCLouvainID)
    }
}

/// UCLouvain user, with minimal information.
#[derive(Debug, Queryable, Insertable, Serialize, Deserialize)]
#[diesel(table_name = users)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct User {
    pub id: i32,
    pub name: String,
}
