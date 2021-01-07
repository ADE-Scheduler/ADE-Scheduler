import click
import pandas as pd
import backend.models as md

import plotly.graph_objects as go
import plotly.express as px

from flask import current_app as app
from flask.cli import with_appcontext
import flask


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


@usage.command()
@with_appcontext
def plot_requests_per_blueprint_hist():

    click.echo("Reading datase...")
    df = md.table_to_dataframe(md.Usage, columns=["datetime", "blueprint"])

    click.echo("Generating plot...")
    df.dropna(subset=["datetime", "blueprint"], inplace=True)

    fig = px.histogram(df, x="datetime", color="blueprint")

    fig.update_layout(
        title="Requests per blueprint",
        xaxis_title="Datetime",
        yaxis_title="Number of requests",
    )

    key = "[PLOT,context=usage]requests_per_blueprint_hist"
    server = app.config["MANAGER"].server
    value = fig.to_json()

    server.set_value(key, value)

    click.echo(f"Successfully created a plot and saved into server with key={key}")
