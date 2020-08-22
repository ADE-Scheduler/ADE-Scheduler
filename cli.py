import random as rnd
import click
from datetime import datetime
from flask import current_app as app
from flask.cli import with_appcontext
from flask_security.cli import users

import backend.models as md


@click.group()
def client():
    """Performs operation on client."""


@client.command()
@with_appcontext
def renew():
    """Renews client's token."""
    cli = app.config['MANAGER'].client
    cli.renew_token()
    click.echo(f'Token successfully renewed. It will expiry in {cli.expire_in():.1f} seconds.')


@client.command()
@with_appcontext
def expire_in():
    """Returns current token expiration time."""
    cli = app.config['MANAGER'].client
    click.echo(f'Token will expiry in {cli.expire_in():.1f} seconds.')


@click.group()
def redis():
    """Performs operations on Redis."""


@redis.command()
@with_appcontext
def update(with_appcontext=False):
    """Updates Redis' tables."""
    mng = app.config['MANAGER']

    mng.update_project_ids()
    mng.update_resource_ids()
    mng.update_resources()
    mng.update_course_resources()
    mng.update_classrooms()
    click.echo(f'Successfully updated the tables on {datetime.now().strftime("%d/%m/%Y at %H:%M:%S")}.')


@redis.command()
@with_appcontext
def flush():
    """Resets Redis, deleting all keys."""
    mng = app.config['MANAGER']
    mng.server.flushdb()
    click.echo('Sucessfully flushed Redis.')


@redis.command()
@click.option('-p', '--pattern', default='*', help='Pattern of the keys. By default, selects all the keys.')
@click.option('-t', '--time', default=-1, type=int, help='Apply an expiry time. If no expiry is specified, simply deletes the keys.')
@click.option('-r', '--random', nargs=2, type=int, help='Apply a random expiry time, between provided lower and upper bounds.')
@with_appcontext
def expire(pattern, time, random):
    """Apply an expiry time to keys in Redis."""
    rd = app.config['MANAGER'].server

    if random:
        def f(key):
            key: rd.expire(key, rnd.randint(200, 400))
    elif time > 0:
        def f(key):
            rd.expire(key, time)
    else:
        def f(key):
            rd.delete(key)

    i = 0
    for key in rd.scan_iter(match=f'{pattern}'):
        f(key)
        i += 1
    click.echo(f'Successfully applied expire to {i} keys.')


@redis.command()
@click.option('-p', '--pattern', default='*', help='Pattern of the keys. By default, selects all the keys.')
@click.option('--session/--no-session', default=False, help='Display the amount of user sessions.')
@click.option('--code/--no-code', default=False, help='Display the amount of unique codes.')
@with_appcontext
def count(pattern, session, code):
    """Counts the number of keys matching a given pattern present in Redis"""
    rd = app.config['MANAGER'].server

    if session:
        count = sum(1 for _ in rd.scan_iter(match='*session*'))
        click.echo(f'There are {count} user sessions.')
    if code:
        count = sum(1 for _ in rd.scan_iter(match='*\[project_id=*\]*'))
        click.echo(f'There are {count} unique codes.')

    if ((code or session) and not pattern == '*') or not (code or session):
        count = sum(1 for _ in rd.scan_iter(match=f'{pattern}'))
        click.echo(f'There are {count} keys matching {pattern}.')


@users.command()
@with_appcontext
def count():
    """Count the number of current users."""
    click.echo(f'There are currently {len(md.User.query.all())} users on ADE-Scheduler.')
