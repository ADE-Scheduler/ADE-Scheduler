//! Structures, enumerates and functions for parsing JSON content
//! from HTTP responses.
//!
//! Note that only useful values are kept.
use crate::models::UCLouvainID;
use serde::{Deserialize, Deserializer};

/// ```rust
/// # use backend::json::{BusinessRoles, BusinessRoleCode};
/// let json = r#"
/// {
///   "businessRoles": {
///     "businessRole": [
///       {
///         "businessRoleId": "00123456",
///         "businessRoleCode": 1,
///         "activity": "AP",
///         "identityId": "12345678"
///       },
///       {
///         "businessRoleId": 12345678,
///         "businessRoleCode": 2,
///         "activity": "AS",
///         "identityId": "12345678"
///       },
///       {
///         "businessRoleId": "01234567",
///         "businessRoleCode": 13,
///         "activity": "AS",
///         "identityId": "12345678"
///       }
///     ]
///   }
/// }"#;
///
/// let roles: BusinessRoles = json.parse().unwrap();
///
/// assert_eq!(roles[0].business_role_code, BusinessRoleCode::Employee);
/// assert_eq!(roles[1].business_role_code, BusinessRoleCode::Student);
/// ```
#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BusinessRoles {
    pub business_roles: BusinessRole,
}

impl std::ops::Deref for BusinessRoles {
    type Target = Vec<BusinessRoleInner>;
    fn deref(&self) -> &Self::Target {
        &self.business_roles.business_role
    }
}

impl std::ops::DerefMut for BusinessRoles {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.business_roles.business_role
    }
}

#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BusinessRole {
    pub business_role: Vec<BusinessRoleInner>,
}

#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BusinessRoleInner {
    pub business_role_id: UCLouvainID,
    #[serde(deserialize_with = "deserialize_role_code")]
    pub business_role_code: BusinessRoleCode,
}

fn deserialize_role_code<'de, D: Deserializer<'de>>(
    deserializer: D,
) -> Result<BusinessRoleCode, D::Error> {
    let code = <u8 as Deserialize>::deserialize(deserializer)?;

    match code {
        1 => Ok(BusinessRoleCode::Employee),
        2 => Ok(BusinessRoleCode::Student),
        _ => Ok(BusinessRoleCode::Unknown),
    }
}

#[derive(Clone, Debug, Default, PartialEq)]
#[repr(u8)]
pub enum BusinessRoleCode {
    Employee = 1,
    Student = 2,
    #[default]
    Unknown = 13,
}

/// ```rust
/// # use backend::json::Employee;
/// use backend::models::UCLouvainID;
///
/// let json = r#"
/// {
///   "person": {
///     "matric_fgs": 87654321,
///     "matric_sap": 12345678,
///     "directory": "L",
///     "lastname": "Lastname",
///     "firstname": "Name",
///     "gender": "M",
///     "lastnameDisplay": "Lastname",
///     "firstnameDisplay": "Firstname",
///     "email": "firstname.lastname@uclouvain.be",
///     "userName": "firstname.lastname"
///   }
/// }"#;
///
/// let employee: Employee = json.parse().unwrap();
/// let fgs = UCLouvainID::new_unchecked(87654321);
///
/// assert_eq!(employee.person.matric_fgs, fgs);
/// ```
#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Employee {
    pub person: Person,
}

#[derive(Clone, Debug, Deserialize)]
pub struct Person {
    pub matric_fgs: UCLouvainID,
}

/// ```rust
/// # use backend::json::Student;
/// use backend::models::UCLouvainID;
///
/// let json = r#"
/// {
///   "lireDossierEtudiantResponse": {
///     "return": {
///       "anneeAcademique": 2023,
///       "codeEtatInscription": 1,
///       "codeStatut": 10,
///       "dateNaissance": "01/09/1970",
///       "etatInscription": "Inscrit",
///       "matricFGS": "00123456",
///       "nom": "Lastname",
///       "noma": "12345678",
///       "prenom": "Firstname",
///       "statut": "Etudiant",
///       "gender": "M",
///       "middlenames": null,
///       "email": "firstname.lastname@student.uclouvain.be"
///     }
///   }
/// }"#;
///
/// let student: Student = json.parse().unwrap();
/// let fgs = UCLouvainID::new_unchecked(123456);
///
/// assert_eq!(
///     student.lire_dossier_etudiant_response._return.matric_fgs,
///     fgs
/// );
/// ```
#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Student {
    pub lire_dossier_etudiant_response: LireDossierEtudiantResponse,
}

#[derive(Clone, Debug, Deserialize)]
pub struct LireDossierEtudiantResponse {
    #[serde(rename = "return")]
    pub _return: Return,
}

#[derive(Clone, Debug, Deserialize)]
pub struct Return {
    #[serde(rename = "matricFGS")]
    pub matric_fgs: UCLouvainID,
}

macro_rules! impl_from_str {
    ($($t:ty)*) => ($(
            impl std::str::FromStr for $t {
                type Err = serde_json::Error;
                fn from_str(s: &str) -> Result<Self, Self::Err> {
                    serde_json::from_str(s)
                }
            }
        )*)
}

impl_from_str!(
    BusinessRoles
    Employee
    Student
);
