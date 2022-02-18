import random as rnd
from datetime import datetime

import click
from flask import current_app as app
from flask.cli import with_appcontext


@click.group()
def redis():
    """Performs operations on Redis."""


@redis.command()
@with_appcontext
def update(with_appcontext=False):
    """Updates Redis' tables."""
    mng = app.config["MANAGER"]

    mng.update_project_ids()
    mng.update_resource_ids()
    mng.update_resources()
    mng.update_course_resources()
    mng.update_classrooms()
    click.secho(
        f'Successfully updated the tables on {datetime.now().strftime("%d/%m/%Y at %H:%M:%S")}.',
        fg="green",
    )


@redis.command()
@with_appcontext
def flush():
    """Resets Redis, deleting all keys."""
    mng = app.config["MANAGER"]
    mng.server.flushdb()
    click.secho("Sucessfully flushed Redis.", fg="green")


@redis.command()
@click.option(
    "-p",
    "--pattern",
    default="*",
    help="Pattern of the keys. By default, selects all the keys.",
)
@click.option(
    "-t",
    "--time",
    default=-1,
    type=int,
    help="Apply an expiry time. If no expiry is specified, simply deletes the keys.",
)
@click.option(
    "-r",
    "--random",
    nargs=2,
    type=int,
    help="Apply a random expiry time, between provided lower and upper bounds.",
)
@with_appcontext
def expire(pattern, time, random):
    """Apply an expiry time to keys in Redis."""
    rd = app.config["MANAGER"].server

    low, high = random

    if random:

        def f(key):
            rd.expire(key, rnd.randint(low, high))

    elif time > 0:

        def f(key):
            rd.expire(key, time)

    else:

        def f(key):
            rd.delete(key)

    i = 0
    for key in rd.scan_iter(match=f"{pattern}"):
        f(key)
        i += 1
    click.secho(f"Successfully applied expire to {i} keys.", fg="green")


@redis.command()
@click.option(
    "-p",
    "--pattern",
    default="*",
    help="Pattern of the keys. By default, selects all the keys.",
)
@click.option(
    "--session/--no-session", default=False, help="Display the amount of user sessions."
)
@click.option(
    "--code/--no-code", default=False, help="Display the amount of unique codes."
)
@with_appcontext
def count(pattern, session, code):
    """Counts the number of keys matching a given pattern present in Redis"""
    rd = app.config["MANAGER"].server

    if session:
        count = sum(1 for _ in rd.scan_iter(match="*session*"))
        click.echo(f"There are {count} user sessions.")
    if code:
        count = sum(1 for _ in rd.scan_iter(match="*\[project_id=*\]*"))
        click.echo(f"There are {count} unique codes.")

    if ((code or session) and not pattern == "*") or not (code or session):
        count = sum(1 for _ in rd.scan_iter(match=f"{pattern}"))
        click.echo(f"There are {count} keys matching {pattern}.")
