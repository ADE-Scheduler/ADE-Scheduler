import click
from flask import current_app as app
from flask.cli import with_appcontext


@click.group()
def client():
    """Performs operation on client."""


@client.command()
@with_appcontext
def renew():
    """Renews client's token."""
    cli = app.config["MANAGER"].client
    cli.renew_token()
    click.secho(
        f"Token successfully renewed. It will expiry in {cli.expire_in():.1f} seconds.",
        fg="green",
    )


@client.command()
@with_appcontext
def expire_in():
    """Returns current token expiration time."""
    cli = app.config["MANAGER"].client
    click.echo(f"Token will expiry in {cli.expire_in():.1f} seconds.")
