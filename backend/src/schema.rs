// @generated automatically by Diesel CLI.

diesel::table! {
    users (id) {
        id -> Int4,
        title -> Varchar,
        body -> Text,
        published -> Bool,
    }
}
