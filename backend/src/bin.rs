use chrono::{NaiveDate, NaiveTime};
use quick_xml::de::from_str;
use serde::de::Error;
use serde::{Deserialize, Deserializer};

// Activities request

#[derive(Debug, Deserialize)]
struct Activities {
    #[serde(rename = "activity")]
    activities: Vec<Activity>,
}

#[derive(Debug, Deserialize)]
struct Activity {
    #[serde(rename = "@id")]
    id: u32,
    #[serde(rename = "@name")]
    name: String,
    #[serde(rename = "@type")]
    _type: String,
    events: Events,
}

#[derive(Debug, Deserialize)]
struct Events {
    #[serde(default)]
    #[serde(rename = "event")]
    events: Vec<Event>,
}

#[derive(Debug, Deserialize)]
struct Event {
    #[serde(rename = "@id")]
    id: u32,
    #[serde(rename = "@name")]
    name: String,
    #[serde(rename = "@endHour")]
    #[serde(deserialize_with = "deserialize_time")]
    end_hour: NaiveTime,
    #[serde(rename = "@startHour")]
    #[serde(deserialize_with = "deserialize_time")]
    start_hour: NaiveTime,
    #[serde(rename = "@date")]
    #[serde(deserialize_with = "deserialize_date")]
    date: NaiveDate,
    #[serde(rename = "@info")]
    info: String,
    #[serde(rename = "@note")]
    note: String,
    #[serde(rename = "eventParticipants")]
    event_participants: EventParticipants,
}

fn deserialize_time<'de, D: Deserializer<'de>>(deserializer: D) -> Result<NaiveTime, D::Error> {
    let s = <&str as Deserialize>::deserialize(deserializer)?;
    NaiveTime::parse_from_str(s, "%H:%M").map_err(D::Error::custom)
}

fn deserialize_date<'de, D: Deserializer<'de>>(deserializer: D) -> Result<NaiveDate, D::Error> {
    let s = <&str as Deserialize>::deserialize(deserializer)?;
    NaiveDate::parse_from_str(s, "%d/%m/%Y").map_err(D::Error::custom)
}

#[derive(Debug, Default, Deserialize)]
struct EventParticipants {
    #[serde(default)]
    #[serde(rename = "eventParticipant")]
    event_participants: Vec<EventParticipant>,
}

#[derive(Debug, Deserialize)]
struct EventParticipant {
    #[serde(rename = "@category")]
    category: Category,
    #[serde(rename = "@name")]
    name: String,
    #[serde(rename = "@id")]
    id: u32,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
enum Category {
    /// Group of courses.
    Trainee,
    /// A teacher.
    Instructor,
    Classroom,
    Equipment,
    /// A course.
    Category5,
    Category6,
    Category7,
    Category8,
}

// Resources request

#[derive(Debug, Deserialize)]
struct Resources {
    #[serde(rename = "resource")]
    resources: Vec<Resource>,
}

#[derive(Debug, Deserialize)]
struct Resource {
    #[serde(rename = "@id")]
    id: u32,
    #[serde(rename = "@name")]
    name: String,
    #[serde(rename = "@category")]
    category: Category,
}

// Project request

#[derive(Debug, Deserialize)]
struct Projects {
    #[serde(rename = "project")]
    projects: Vec<Project>,
}

#[derive(Debug, Deserialize)]
struct Project {
    #[serde(rename = "@id")]
    id: u32,
    #[serde(rename = "@name")]
    name: String,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let file = std::env::args().nth(1).unwrap();

    let text = std::fs::read_to_string(&file)?;

    let doc: Projects = from_str(text.as_str())?;

    println!("{:#?}", doc);

    Ok(())
}
