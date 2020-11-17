import click


@click.group()
def client():
    """Performs operation on client."""


import cli.client


@click.group()
def redis():
    """Performs operations on Redis."""


import cli.redis


from flask_security.cli import users
import cli.users


@click.group()
def schedules():
    """Performs operations with the schedules"""


import cli.schedules


@click.group()
def sql():
    """Performs operations on the SQL database."""


import cli.sql


@click.group()
def usage():
    """Performs operations on the Usage table."""
    pass


import cli.usage


@click.group()
def api_usage():
    """Performs operations on the ApiUsage table."""
    pass


import cli.api_usage
