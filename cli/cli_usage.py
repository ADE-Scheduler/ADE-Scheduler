import click
import pandas as pd
import backend.models as md

from flask import current_app as app
from flask.cli import with_appcontext


@click.group()
def usage():
    """Performs operations on the Usage table."""
    pass


@usage.command()
@with_appcontext
def stats():
    threshold = 100
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)

    click.echo("Reading datase...")
    df = md.table_to_dataframe(md.Usage, columns=["url", "speed", "blueprint"])

    with app.test_request_context():
        host_url = flask.request.host_url

    host_url = "https://ade-scheduler.info.ucl.ac.be/"

    click.echo(
        f"Computing all requests matching {host_url}<blueprint>/<request>)"
        f" and appearing at least {threshold: d} times..."
    )

    endpoints = (
        df["url"]
        .str.replace(host_url[:-1], "")
        .str.extract(r"^\/\w+\/(\w+)", expand=False)
    )
    df["url"] = endpoints
    req_stats = (
        df.groupby(["blueprint", "url"])
        .filter(lambda x: len(x) > threshold)
        .groupby(["blueprint", "url"])
    )

    click.echo(req_stats.speed.describe())
    click.echo(host_url)
