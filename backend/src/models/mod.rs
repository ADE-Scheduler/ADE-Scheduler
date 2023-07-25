use super::schema::users;
use diesel::prelude::*;
use serde::{Deserialize, Serialize};
use std::fmt;

/// FGS unique identifier for UCLouvain members.
///
/// FGS is usually an 8-digits string, which can contain leading zeros.
/// `FGS::to_string` solve this problem by appending leading zeros if needed,
/// but uses one `u32` for storage, which is far better than a string.
///
/// ```rust
/// # use backend::models::FGS;
/// let fgs = FGS(00123456);
/// assert_eq!("00123456", fgs.to_string());
pub struct FGS(pub u32);


impl fmt::Display for FGS {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:08}", self.0)
    }
}

#[derive(Debug, Queryable, Insertable, Serialize, Deserialize)]
#[diesel(table_name = users)]
pub struct User {
    pub id: i32,
    pub name: String,
}
