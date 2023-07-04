# Backend

[![Website](https://img.shields.io/website?label=documentation&up_message=online&url=https%3A%2F%2Fade-scheduler.github.io%2FADE-Scheduler)](https://ade-scheduler.github.io/ADE-Scheduler)

This folder contains Rust code to execute the backend server.

To install Rust, please refer to <https://www.rust-lang.org/tools/install>.

## Database

ADE Scheduler uses a database to store information about users, schedules,
and more.

*WIP section based on [this blog post](https://blog.logrocket.com/create-web-app-rust-rocket-diesel/).*

### Setup

*You should only perform this setup once.*

First, you need to install
[PostgreSQL](https://www.postgresql.org/download/) and the Diesel CLI:

```bash
cargo install diesel_cli --no-default-features --features postgres
```

Next, you must define the database URI in a `backend/.env` file, e.g.:

```bash
DATABASE_URL=postgresql://postgres@localhost/ade-database
```

Finally, make sure this database exists,
and is clean (no prior database with the same name).
Read
[this article](https://phoenixnap.com/kb/postgresql-drop-database#:~:text=The%20first%20method%20to%20remove,execute%20the%20DROP%20DATABASE%20command.)
to know how to drop and create a database.

### Migration

You can migrate the database to the latest version with:

```bash
diesel migration run
```

## Running the server

To run the server in debug mode, simply execute this command:

```bash
cargo run
```

> NOTE: compilation can by quite slow,
so prefer using `cargo check` to verify that the code compile.

### Hot reloading

If you want to automatically recompile your code on changes, you can use
`cargo-watch`.

First, you need to install it:

```bash
cargo install cargo-watch
```

Then, you can run the server with `cargo-watch`:

```bash
cargo watch -x run
```

## Formatting the code

Rust code can be formatted with its own formatter. Since we used nightly features,
you need to install the nightly toolchain with:

```bash
rustup toolchain install nightly
```

Then, you can format the code with:

```bash
cargo +nightly fmt
```

## Linting the code

The same applies for Rust's linter:

```bash
cargo +nightly clippy
```

## Generating the documentation

You can also generate the documentation with:

```bash
cargo doc --lib --no-deps --open
```

> NOTE: you can omit the `--open` flag if you don't want to open a new tab on
each build.
