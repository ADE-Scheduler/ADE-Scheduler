use super::schema::posts;
use diesel::{prelude::*};
use serde::{Serialize, Deserialize};

#[derive(Queryable, Insertable, Serialize, Deserialize)]
#[diesel(table_name = users)]
pub struct Users {
    pub id: i32,
    pub title: String,
    pub body: String,
    pub published: bool,
}
