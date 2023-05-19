# Backend

This folder contains Rust code to execute the backend server.

To install Rust, please refer to <https://www.rust-lang.org/tools/install>.

## Running the server

To run the server in debug mode, simply execute this command:

```bash
cargo run
```

> NOTE: compilation can by quite slow,
so prefer using `cargo check` to verify that the code compile.

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
