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
/// let fgs = UCLouvainID::new_unchecked(12345678);
/// assert_eq!("12345678", fgs.to_string());
///
/// // Accepts leading zeros;
/// let fgs = UCLouvainID::new_unchecked(00123456);
/// assert_eq!("00123456", fgs.to_string());
#[derive(Clone, Debug, PartialEq)]
pub struct UCLouvainID(u32);

pub type FGS = UCLouvainID;
pub type NOMA = UCLouvainID;

impl UCLouvainID {
    /// Maximal values, as ids are always 8-digits long strings.
    pub const MAX: u32 = 99_999_999;
    
    /// Creates a new [`UCLouvainID`] from a given id,
    /// and returns an error if `id` is greater than [`UCLouvainID::MAX`].
    #[inline(always)]
    pub fn new(id: u32) -> Result<Self, &'static str> {
        if id > Self::MAX {
            Err("id cannot be greater than 99_999_999")
        } else {
            Ok(Self(id))
        }
    }
    
    #[inline(always)]
    /// Creates a new [`UCLouvainID`] from a given id,
    /// and never checks if `id` is greater than [`UCLouvainID::MAX`].
    pub fn new_unchecked(id: u32) -> Self {
        UCLouvainID(id)
    }
}

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
            .and_then(|id| UCLouvainID::new(id).map_err(de::Error::custom))
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
