// @generated automatically by Diesel CLI.

diesel::table! {
    schedules (id) {
        id -> Int4,
        name -> Nullable<Varchar>,
        codes -> Nullable<Text>,
        user_id -> Int4,
    }
}

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

diesel::joinable!(schedules -> users (user_id));

diesel::allow_tables_to_appear_in_same_query!(
    schedules,
    users,
);
