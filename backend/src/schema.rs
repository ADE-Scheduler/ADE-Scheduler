// @generated automatically by Diesel CLI.

diesel::table! {
    users (id) {
        id -> Int4,
        fgs -> Int4,
        firstname -> Varchar,
        lastname -> Varchar,
        email -> Varchar,
        created_at -> Timestamp,
        last_seen_at -> Timestamp,
    }
}
