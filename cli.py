import random as rnd
import pickle as pkl
import click
from datetime import datetime
from flask import current_app as app
from flask.cli import with_appcontext
from flask_security.cli import users
from sqlalchemy import func
import pandas as pd

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
    click.secho(f'Token successfully renewed. It will expiry in {cli.expire_in():.1f} seconds.', fg='green')


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
    click.secho(f'Successfully updated the tables on {datetime.now().strftime("%d/%m/%Y at %H:%M:%S")}.', fg='green')


@redis.command()
@with_appcontext
def flush():
    """Resets Redis, deleting all keys."""
    mng = app.config['MANAGER']
    mng.server.flushdb()
    click.secho('Sucessfully flushed Redis.', fg='green')


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
    click.secho(f'Successfully applied expire to {i} keys.', fg='green')


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
    click.echo(f'There are currently {md.User.query.filter(None != md.User.confirmed_at).count()} '
               f'(confirmed) users on ADE-Scheduler.')


@users.command()
@with_appcontext
def stats():
    """Returns some statistics about users."""
    confirmed_users = md.User.query.filter(None != md.User.confirmed_at).all()
    df = pd.DataFrame([[user.confirmed_at.strftime('%Y/%m/%d'), user.email, len(user.schedules)]
                      for user in confirmed_users], columns=['date', 'email', 'n_schedules'])

    click.echo('Accounts created per day:')
    for date, count in df.groupby('date').size().iteritems():
        click.echo(f'\t{date}: {count}')
    click.echo(f'\tTotal: {len(confirmed_users)}')

    click.echo('Email address domains:')

    df['email'] = df['email'].apply(lambda s: s.split('@')[1])

    for domain, count in df.groupby('email').size().iteritems():
        click.echo(f'\t{domain}: {count}')

    click.echo('Schedules count stats:')
    description = df['n_schedules'].describe()
    description['count'] = df['n_schedules'].sum()
    for x, value in description.iteritems():
        click.echo(f'\t{x}: {value}')


@click.group()
def sql():
    """Performs operations on the SQL database."""


@sql.command()
@with_appcontext
def init():
    """Initialization of the SQL database."""
    db = app.config['MANAGER'].database
    db.create_all()
    click.echo('Successfully initiliazed the database.')


@sql.command()
@click.option('-o', '--output', default='database.dump', help='Output file.')
@with_appcontext
def dump(output):
    """Dumps the database."""
    tables = [md.Role, md.User, md.Schedule, md.Link, md.Property, md.Usage]

    with open(output, 'wb') as f:
        for table in tables:
            rows = table.query.all()
            for row in rows:
                pkl.dump(row, f, pkl.HIGHEST_PROTOCOL)
    click.echo(f'Sucessfully dumped data to file "{output}".')


@sql.command()
@click.option('-i', '--input', default='database.dump', help='Input file.')
@with_appcontext
def load(input):
    """
    Loads the database from a dumpfile.
    Tested with PostgreSQL, MySQL & SQLite.
    """
    db = app.config['MANAGER'].database
    tables = [md.Role, md.User, md.Schedule, md.Link, md.Property, md.Usage]

    with open(input, 'rb') as f:
        with db.session.no_autoflush:
            while True:
                try:
                    row = pkl.load(f)
                    db.session.merge(row)
                except EOFError:
                    break

    if db.session.bind.dialect.name == 'postgresql':
        # https://stackoverflow.com/questions/37970743/postgresql-unique-violation-7-error-duplicate-key-value-violates-unique-const/37972960#37972960
        for table in tables:
            val = db.session.query(func.max(table.id)).scalar()
            name = table.__tablename__
            if val:
                db.session.execute(f"SELECT setval(pg_get_serial_sequence('{name}', 'id'), {val+1}, false) FROM {name};")

    db.session.commit()
    click.echo(f'Successfully loaded data from file "{input}".')


@sql.command()
@with_appcontext
def fix():
    db = app.config['MANAGER'].database
    for row in md.Property.query.all():
        if row.user is None:
            db.session.delete(row)
    db.session.commit()
    click.secho('Database cleaned !', fg='green')
