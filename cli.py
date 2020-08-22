import random as rnd
import click
from flask import current_app as app
from flask.cli import with_appcontext


@click.group()
def client():
    """Performs operation on client."""


@client.command()
@with_appcontext
def renew_token():
    """Renews client's token."""
    cli = app.config['MANAGER'].client
    cli.renew_token()
    click.echo(f'Token successfully renewed. It will expiry in {cli.expire_in():.1f} seconds.')


@client.command()
@with_appcontext
def token_expire_in():
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


@redis.command()
@with_appcontext
def flush():
    """Resets Redis, deleting all keys."""
    mng = app.config['MANAGER']
    mng.server.flushdb()


@redis.command()
@click.option('-p', '--pattern', default='*', help='Pattern of the keys. By default, selects all the keys.')
@click.option('-t', '--time', default=-1, type=int, help='Apply an expiry time. If no expiry is specified, simply deletes the keys.')
@click.option('-r', '--random', nargs=2, type=int, help='Apply a random expiry time, between provided lower and upper bounds.')
@with_appcontext
def expire(pattern, time, random):
    """Apply an expiry time to keys in Redis."""
    rd = app.config['MANAGER'].server

    for key in rd.scan_iter(match=f'{pattern}'):
        if random:
            rd.expire(key, rnd.randint(200, 400))
        elif time > 0:
            rd.expire(key, time)
        else:
            rd.delete(key)


@redis.command()
@click.option('-p', '--pattern', default='*', help='Pattern of the keys. By default, selects all the keys.')
@with_appcontext
def count(pattern):
    """Counts the number of keys matching a given pattern present in Redis"""
    rd = app.config['MANAGER'].server

    count = sum(1 for _ in rd.scan_iter(match=f'{pattern}'))
    click.echo(f'There are {count} keys matching {pattern}.')
