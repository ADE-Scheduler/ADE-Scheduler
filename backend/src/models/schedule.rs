
use std::collections::{HashSet, Hashmap};

use diesel::prelude::*;

use crate::schema::shedules;

use super::User;

#[derive(Queryable, Selectable, Identifiable, Associations, Debug, PartialEq)]
#[diesel(belongs_to(User))]
#[diesel(table_name = schedules)]
pub struct Schedule {
    pub name: Option<String>
    pub codes: HashMap<String, Vec<String>,
}
