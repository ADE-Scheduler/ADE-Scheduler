use rocket_db_pools::{deadpool_redis, Database};

pub use redis::*;
pub use rocket_db_pools::Connection;

#[derive(Database)]
#[database("redis")]
pub struct Redis(deadpool_redis::Pool);
