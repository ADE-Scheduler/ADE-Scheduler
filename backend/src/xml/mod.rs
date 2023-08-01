//! Structures, enumerates and functions for parsing XML content
//! from HTTP responses.
//!
//! Note that only useful values are kept.

use std::collections::HashMap;

use chrono::{NaiveDate, NaiveTime};
use rocket_okapi::JsonSchema;
use serde::{de::Error, Deserialize, Deserializer, Serialize};

/// Convenience trait for building requests with [`reqwest::RequestBuilder`].
pub trait Parameters {
    /// Return the query parameters needed to obtain a valid XML response.
    ///
    /// ```
    /// # use backend::xml::{Parameters, Resources};
    /// # use backend::ade::Token;
    /// # use backend::error::Result;
    /// use reqwest::Client;
    ///
    /// async fn get_resources(client: &Client, token: &Token) -> Result<Resources> {
    ///     let response = client
    ///         .get("some/api/url/")
    ///         .bearer_auth(token.access_token.clone())
    ///         .query(Resources::parameters())
    ///         .send()
    ///         .await?;
    ///
    ///     let resources = response.text().await?.parse()?;
    ///
    ///     Ok(resources)
    /// }
    fn parameters() -> &'static [(&'static str, &'static str)];
}

/// Result from a `getActivities` request.
///
/// Minimal level of details required: 17 (maximum).
///
/// ```
/// # use backend::xml::Activities;
/// let xml = r#"
/// <?xml version="1.0" encoding="UTF-8"?>
/// <activities>
/// 	<activity id="19833" name="LEPL1104=E" type="Examen écrit" folderId="10419" url="" size="100" repetition="1" lastUpdate="05/09/2023 09:25" creation="10/03/2019 09:25" lastSlot="14" lastDay="0" lastWeek="39" firstSlot="2" firstDay="0" firstWeek="39" additionalResources="0" durationInMinutes="180" nbEventsPlaced="1" nbEvents="1" duration="180" email="" weight="0" seatsLeft="372 (09-01-2023)" maxSeats="372*3=1116" info="Notes de séances pour juin 2023 - Répartition en auditoires" codeZ="" codeY="" codeX="" timezone="" code="MÉTHODES NUMÉRIQUES" color="255,255,255" isActive="true" isNotSameDay="false" isGrouped="false" isAligned="false" isSuccessiveDays="false" ownerId="96" owner="lauwimana">
/// 		<events>
/// 			<event id="111290" activityId="19833" session="0" repetition="0" name="LEPL1104=E" endHour="11:30" startHour="08:30" date="12/06/2023" absoluteSlot="17474" slot="2" day="0" week="39" additionalResources="0" duration="12" info="Notes de séances pour juin 2023 - Répartition en auditoires" note="Répartition en auditoires - JUIN 2023 :&#10;- A.01: de Aarab à  Crespo Colsa&#10;- A.02: de Crothers à  Gaudin&#10;- A.03 : de Gengoux à  Lacheron&#10;- A.10 : de Lallemand à  Zhabrailov" color="255,255,255" isLockPosition="false" oldDuration="12" oldSlot="2" oldDay="4" oldWeek="39" lastUpdate="05/09/2023 09:25" creation="02/08/2023 17:01" isLockResources="false" isSoftKeepResources="false" isNoteLock="false" isStrongLock="false">
/// 				<eventParticipants>
/// 					<eventParticipant fromWorkflow="false" nodeId="141979" nodeOrId="-1" quantity="1" category="trainee" name="fsa11ba" id="7851"/>
/// 					<eventParticipant fromWorkflow="false" nodeId="258824" nodeOrId="-1" quantity="1" category="trainee" name="Approfondissement STAT12" id="16593"/>
/// 					<eventParticipant fromWorkflow="false" nodeId="258825" nodeOrId="-1" quantity="1" category="trainee" name="Approfondissement STAT13" id="16598"/>
/// 					<eventParticipant fromWorkflow="false" nodeId="150877" nodeOrId="-1" quantity="1" category="category5" name="LEPL1104" id="4464"/>
/// 					<eventParticipant fromWorkflow="true" nodeId="171232" nodeOrId="171231" quantity="1" category="classroom" name="A.01 SCES" id="848"/>
/// 					<eventParticipant fromWorkflow="false" nodeId="259905" nodeOrId="259632" quantity="1" category="classroom" name="A.03 SCES" id="2320"/>
/// 					<eventParticipant fromWorkflow="false" nodeId="150881" nodeOrId="150880" quantity="1" category="instructor" name="Legat Vincent" id="497"/>
/// 					<eventParticipant fromWorkflow="true" nodeId="171233" nodeOrId="171231" quantity="1" category="classroom" name="A.02 SCES" id="2318"/>
/// 					<eventParticipant fromWorkflow="true" nodeId="171240" nodeOrId="171231" quantity="1" category="classroom" name="A.10 SCES" id="2321"/>
/// 				</eventParticipants>
/// 				<additional/>
/// 			</event>
/// 		</events>
/// 		<resources activityId="19833">
/// 			<and load="1.0" quantity="1" nodeId="141979" id="7851" name="fsa11ba" path="EPL.EPL Cycle 1.EPL Bacheliers.FSA1BA." category="trainee" isGroup="true"/>
/// 			<and load="1.0" quantity="1" nodeId="258824" id="16593" name="Approfondissement STAT12" path="SC.SC Cycle 1.SC Mineures.Approfondissement en statistique et science des données." category="trainee" isGroup="false"/>
/// 			<and load="1.0" quantity="1" nodeId="258825" id="16598" name="Approfondissement STAT13" path="SC.SC Cycle 1.SC Mineures.Approfondissement en statistique et science des données." category="trainee" isGroup="false"/>
/// 			<and load="1.0" quantity="1" nodeId="150877" id="4464" name="LEPL1104" path="SST - EPL.LEPL." category="category5" isGroup="false"/>
/// 			<or isContinuous="false" category="instructor" quantity="1" id="150880">
/// 				<and load="1.0" quantity="1" nodeId="150881" id="497" name="Legat Vincent" path="Personnel UCL.L." category="instructor" isGroup="false"/>
/// 			</or>
/// 			<or isContinuous="false" category="classroom" quantity="1" id="259632">
/// 				<and load="1.0" quantity="1" nodeId="259905" id="2320" name="A.03 SCES" path="Site de Louvain-la-Neuve.Zone Sciences et Technologies.Auditoires des Sciences (SCES)." category="classroom" isGroup="false"/>
/// 			</or>
/// 			<orRequest isContinuous="false" category="classroom" quantity="3" id="171231" senderId="96" copyByMail="false" message="" subject="Requàªte">
/// 				<recipients managerUsers="true"/>
/// 				<and load="1.0" quantity="1" nodeId="171232" id="848" name="A.01 SCES" path="Site de Louvain-la-Neuve.Zone Sciences et Technologies.Auditoires des Sciences (SCES)." category="classroom" isGroup="false"/>
/// 				<and load="1.0" quantity="1" nodeId="171233" id="2318" name="A.02 SCES" path="Site de Louvain-la-Neuve.Zone Sciences et Technologies.Auditoires des Sciences (SCES)." category="classroom" isGroup="false"/>
/// 				<and load="1.0" quantity="1" nodeId="171240" id="2321" name="A.10 SCES" path="Site de Louvain-la-Neuve.Zone Sciences et Technologies.Auditoires des Sciences (SCES)." category="classroom" isGroup="false"/>
/// 			</orRequest>
/// 		</resources>
/// 		<rights othersRights="read" groupRights="rw" userRights="none" group="root" user="root" profileName="W_ADE / U_Appariteurs / R_OTHER" profileId="118"/>
/// 	</activity>
/// </activities>"#;
///
/// let activities: Activities = xml.parse().unwrap();
///
/// assert_eq!(activities[0].name, "LEPL1104=E");
/// ```
#[allow(clippy::tabs_in_doc_comments)]
#[derive(Clone, Debug, Deserialize, Serialize, JsonSchema)]
pub struct Activities {
    #[serde(rename(deserialize = "activity"))]
    #[schemars(rename = "activities")]
    pub activities: Vec<Activity>,
}

impl Parameters for Activities {
    fn parameters() -> &'static [(&'static str, &'static str)] {
        &[("tree", "false"), ("detail", "17")]
    }
}

/// An activity.
///
/// In ADE, activities are mostly recurring events using
/// the same name.
///
/// For example, under the course named "LEPL1104", the activity
/// "LEPL1104_Q1" is for all the pratical sessions (`_`) of the 1st session
/// (`Q1`).
///
/// Sometimes, the activity type is also specified by the `_type` field.
#[derive(Clone, Debug, Deserialize, Serialize, JsonSchema)]
pub struct Activity {
    #[serde(rename(deserialize = "@id"))]
    #[schemars(rename = "id")]
    pub id: u32,
    #[serde(rename(deserialize = "@name"))]
    #[schemars(rename = "name")]
    pub name: String,
    #[serde(rename(deserialize = "@type", serialize = "type"))]
    #[schemars(rename = "type")]
    pub _type: String,
    pub events: Events,
}

/// Events containers.
#[derive(Clone, Debug, Deserialize, Serialize, JsonSchema)]
pub struct Events {
    #[serde(default)]
    #[serde(rename(deserialize = "event"))]
    #[schemars(rename = "events")]
    pub events: Vec<Event>,
}

/// A calendar event, with some information.
#[derive(Clone, Debug, Deserialize, Serialize, JsonSchema)]
pub struct Event {
    #[serde(rename(deserialize = "@id"))]
    #[schemars(rename = "id")]
    pub id: u32,
    #[serde(rename(deserialize = "@name"))]
    #[schemars(rename = "name")]
    pub name: String,
    #[serde(rename(deserialize = "@endHour"))]
    #[serde(deserialize_with = "deserialize_time")]
    #[schemars(rename = "end_hour")]
    pub end_hour: NaiveTime,
    #[serde(rename(deserialize = "@startHour"))]
    #[serde(deserialize_with = "deserialize_time")]
    #[schemars(rename = "start_hour")]
    pub start_hour: NaiveTime,
    #[serde(rename(deserialize = "@date"))]
    #[serde(deserialize_with = "deserialize_date")]
    #[schemars(rename = "date")]
    pub date: NaiveDate,
    #[serde(rename(deserialize = "@info"))]
    #[schemars(rename = "info")]
    pub info: String,
    #[serde(rename(deserialize = "@note"))]
    #[schemars(rename = "note")]
    pub note: String,
    #[serde(rename(deserialize = "eventParticipants"))]
    #[schemars(rename = "event_participants")]
    pub event_participants: EventParticipants,
}

fn deserialize_time<'de, D: Deserializer<'de>>(deserializer: D) -> Result<NaiveTime, D::Error> {
    let s = <&str as Deserialize>::deserialize(deserializer)?;
    NaiveTime::parse_from_str(s, "%H:%M").map_err(D::Error::custom)
}

fn deserialize_date<'de, D: Deserializer<'de>>(deserializer: D) -> Result<NaiveDate, D::Error> {
    let s = <&str as Deserialize>::deserialize(deserializer)?;
    NaiveDate::parse_from_str(s, "%d/%m/%Y").map_err(D::Error::custom)
}

/// Event participants containers.
#[derive(Clone, Debug, Default, Deserialize, Serialize, JsonSchema)]
pub struct EventParticipants {
    #[serde(default)]
    #[serde(rename(deserialize = "eventParticipant"))]
    #[schemars(rename = "event_participants")]
    pub event_participants: Vec<EventParticipant>,
}

/// A participant to an event.
///
/// This can be any variant of [`Category`], like teacher
/// ([`Category::Instructor`]), a room ([`Category::Classroom`]),
/// or a main course name ([`Category::Category5`]).
#[derive(Clone, Debug, Deserialize, Serialize, JsonSchema)]
pub struct EventParticipant {
    #[serde(rename(deserialize = "@category"))]
    #[schemars(rename = "category")]
    pub category: Category,
    #[serde(rename(deserialize = "@name"))]
    #[schemars(rename = "name")]
    pub name: String,
    #[serde(rename(deserialize = "@id"))]
    #[schemars(rename = "id")]
    pub id: u32,
}

/// Enumeration of all categories returned by ADE's API.
#[derive(Clone, Debug, Deserialize, Serialize, JsonSchema)]
#[serde(rename_all = "camelCase")]
pub enum Category {
    /// Group of courses, like a course program.
    Trainee,
    /// A teacher.
    Instructor,
    /// A classroom.
    Classroom,
    /// Some equipment, fourniture, etc.
    Equipment,
    /// A course name.
    Category5,
    /// A course name.
    ///
    /// Only a very small percent of course names are in this
    /// category, and most of the other courses are [`Category::Category6`].
    Category6,
    /// Maintenance activity.
    ///
    /// Very few activities are under this name.
    /// Catering and cleaning are in this category.
    Category7,
    /// Unknown category.
    Category8,
}

/// Result from a `getResources` request with no filter on category types.
///
/// Minimal level of details required: 3.
///
/// ```
/// # use backend::xml::Resources;
/// let xml = r#"
/// <?xml version="1.0" encoding="UTF-8"?>
/// <resources>
/// 	<resource id="8362" name="KINE21M_G8-A" path="FSM.FSM Cycle 2.FSM Masters 60.KINE2M1.KINE21M.KINE21M_G.KINE21M_G8." category="trainee" isGroup="false" type="" email="" url="" consumer="false" size="1" lastUpdate="10/25/2022 09:06" creation="08/11/2020 14:09" lastSlot="28" lastDay="5" lastWeek="50" firstSlot="0" firstDay="0" firstWeek="1" durationInMinutes="25680" nbEventsPlaced="204" availableQuantity="1" number="1" fatherName="KINE21M_G8" fatherId="7449" info="" codeZ="" codeY="" codeX="" manager="" jobCategory="" timezone="" fax="" telephone="" country="" city="" state="" zipCode="" address2="" address1="" code="" color="255,255,255" levelAccess="read" owner="walravensc">
/// 		<allMembers/>
/// 		<memberships/>
/// 		<constraints quality="100" distribution="100">
/// 			<costs>
/// 				<cost value="0.0" name="PrioritéSomebody" id="4"/>
/// 				<cost value="0.0" name="coût CONFORT" id="19"/>
/// 				<cost value="0.0" name="Coût virtuel" id="21"/>
/// 			</costs>
/// 			<caracteristics/>
/// 			<counters isUseCounter="false"/>
/// 			<setupTimes/>
/// 			<sites/>
/// 			<countersMoving isUseCounterMoving="false"/>
/// 		</constraints>
/// 		<rights othersRights="read" groupRights="rw" userRights="none" group="root" user="root" profileName="Etudiants FSM" profileId="103"/>
/// 	</resource>
/// </resources>"#;
///
/// let resources: Resources = xml.parse().unwrap();
///
/// assert_eq!(resources[0].name, "KINE21M_G8-A");
/// ```
#[allow(clippy::tabs_in_doc_comments)]
#[derive(Clone, Debug, Deserialize, Serialize, JsonSchema)]
pub struct Resources {
    #[serde(rename(deserialize = "resource"))]
    #[schemars(rename = "resources")]
    pub resources: Vec<Resource>,
}

impl Resources {
    /// Consumes self and returns
    /// a hashmap that maps resource names
    /// to the full resources.
    pub fn into_hashmap(self) -> HashMap<String, Resource> {
        let mut map = HashMap::with_capacity(self.resources.len());
        self.resources.into_iter().for_each(|resource| {
            map.insert(resource.name.clone(), resource);
        });
        map
    }
}

impl Parameters for Resources {
    fn parameters() -> &'static [(&'static str, &'static str)] {
        &[("tree", "false"), ("detail", "3")]
    }
}

/// A resource.
#[derive(Clone, Debug, Deserialize, Serialize, JsonSchema)]
pub struct Resource {
    #[serde(rename(deserialize = "@id"))]
    #[schemars(rename = "id")]
    pub id: u32,
    #[serde(rename(deserialize = "@name"))]
    #[schemars(rename = "name")]
    pub name: String,
    #[serde(rename(deserialize = "@category"))]
    #[schemars(rename = "category")]
    pub category: Category,
}

/// Result from a `getProjects` request.
///
/// Minimal level of details required: 2.
///
/// ```
/// # use backend::xml::Projects;
/// let xml = r#"
/// <?xml version="1.0" encoding="UTF-8"?>
/// <projects>
/// 	<project id="19" name="2022-2023" uid="1664978691092" version="670"/>
/// </projects>"#;
///
/// let projects: Projects = xml.parse().unwrap();
///
/// assert_eq!(projects[0].name, "2022-2023");
/// ```
#[allow(clippy::tabs_in_doc_comments)]
#[derive(Clone, Debug, Deserialize, Serialize, JsonSchema)]
pub struct Projects {
    #[serde(rename(deserialize = "project"))]
    #[schemars(rename = "projects")]
    pub projects: Vec<Project>,
}

impl Parameters for Projects {
    fn parameters() -> &'static [(&'static str, &'static str)] {
        &[("detail", "2")]
    }
}

/// A project for a given academic year.
///
/// The name is simply the year (start-end) for this project.
/// The id is used to request activities from a given year to the API.
#[derive(Clone, Debug, Deserialize, Serialize, JsonSchema)]
pub struct Project {
    #[serde(rename(deserialize = "@id"))]
    #[schemars(rename = "id")]
    pub id: u32,
    #[serde(rename(deserialize = "@name"))]
    #[schemars(rename = "name")]
    pub name: String,
}

macro_rules! impl_from_str {
    ($($t:ty)*) => ($(
            impl std::str::FromStr for $t {
                type Err = quick_xml::de::DeError;
                fn from_str(s: &str) -> Result<Self, Self::Err> {
                    quick_xml::de::from_str(s)
                }
            }
        )*)
}

impl_from_str!(
    Activity
    Activities
    Event
    EventParticipant
    EventParticipants
    Events
    Project
    Projects
    Resource
    Resources
);

macro_rules! impl_deref_mut {
    ($($t:ty, $attr:tt, $target:ty)*) => ($(
            impl std::ops::Deref for $t {
                type Target = $target;
                fn deref(&self) -> &Self::Target {
                    &self.$attr
                }
            }

            impl std::ops::DerefMut for $t {
                fn deref_mut(&mut self) -> &mut Self::Target {
                    &mut self.$attr
                }
            }
        )*)
}

impl_deref_mut!(
    Activities, activities, Vec<Activity>
    Events, events, Vec<Event>
    EventParticipants, event_participants, Vec<EventParticipant>
    Projects, projects, Vec<Project>
    Resources, resources, Vec<Resource>
);
