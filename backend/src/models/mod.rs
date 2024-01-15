//! Database models.

use rocket_db_pools::{
    diesel::{PgPool},
    Database,
};

mod user;
mod schedule;

pub use user::{NewUser, User, UCLouvainID, FGS, NOMA};
pub use schedule::Schedule;

pub use rocket_db_pools::Connection;

#[derive(Database)]
#[database("ade-database")]
pub struct Db(PgPool);

