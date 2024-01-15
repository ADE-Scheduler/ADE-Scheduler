-- Your SQL goes here
CREATE TABLE schedules (
  id SERIAL PRIMARY KEY,
  name VARCHAR,
  codes TEXT,
  user_id SERIAL REFERENCES users(id)
);
