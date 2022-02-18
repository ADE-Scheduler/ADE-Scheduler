import pickle as pkl

import click
from flask import current_app as app
from flask.cli import with_appcontext
from sqlalchemy import func

import backend.models as md


@click.group()
def sql():
    """Performs operations on the SQL database."""


@sql.command()
@with_appcontext
def init():
    """Initialization of the SQL database."""
    db = app.config["MANAGER"].database
    db.create_all()
    click.echo("Successfully initiliazed the database.")


@sql.command()
@click.option("-o", "--output", default="database.dump", help="Output file.")
@with_appcontext
def dump(output):
    """Dumps the database."""
    tables = [
        md.Role,
        md.User,
        md.Schedule,
        md.Link,
        md.Property,
        md.Usage,
        md.ApiUsage,
    ]

    with open(output, "wb") as f:
        for table in tables:
            rows = table.query.all()
            for row in rows:
                pkl.dump(row, f, pkl.HIGHEST_PROTOCOL)
    click.echo(f'Sucessfully dumped data to file "{output}".')


@sql.command()
@click.option("-i", "--input", default="database.dump", help="Input file.")
@with_appcontext
def load(input):
    """
    Loads the database from a dumpfile.
    Tested with PostgreSQL, MySQL & SQLite.
    """
    db = app.config["MANAGER"].database
    tables = [
        md.Role,
        md.User,
        md.Schedule,
        md.Link,
        md.Property,
        md.Usage,
        md.ApiUsage,
    ]

    with open(input, "rb") as f:
        with db.session.no_autoflush:
            while True:
                try:
                    row = pkl.load(f)
                    db.session.merge(row)
                except EOFError:
                    break

    if db.session.bind.dialect.name == "postgresql":
        # https://stackoverflow.com/questions/37970743/postgresql-unique-violation-7-error-duplicate-key-value-violates-unique-const/37972960#37972960
        for table in tables:
            val = db.session.query(func.max(table.id)).scalar()
            name = table.__tablename__
            if val:
                db.session.execute(
                    f"SELECT setval(pg_get_serial_sequence('{name}', 'id'), {val+1}, false) FROM {name};"
                )

    db.session.commit()
    click.echo(f'Successfully loaded data from file "{input}".')


@sql.command()
@with_appcontext
def fix():
    db = app.config["MANAGER"].database
    for row in md.Property.query.all():
        if row.user is None:
            db.session.delete(row)
    db.session.commit()
    click.secho("Database cleaned !", fg="green")
