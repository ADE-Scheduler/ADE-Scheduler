import click
import pandas as pd
import numpy as np
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

    click.echo("Reading database...")
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

    click.echo("Reading database...")
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


@usage.command()
@with_appcontext
def plot_views_per_blueprint_hist():

    click.echo("Reading database...")
    df = md.table_to_dataframe(md.Usage, columns=["datetime", "blueprint", "path"])

    click.echo("Generating plot...")
    df.dropna(subset=["datetime", "blueprint"], inplace=True)

    index = np.logical_or.reduce(
        [df.path.endswith(f"/{blueprint}/") for blueprint in df.blueprint.unique()]
    )

    df = df[index]

    fig = px.histogram(df, x="datetime", color="blueprint")

    fig.update_layout(
        title="Views per blueprint",
        xaxis_title="Datetime",
        yaxis_title="Number of views",
    )

    key = "[PLOT,context=usage]views_per_blueprint_hist"
    server = app.config["MANAGER"].server
    value = fig.to_json()

    server.set_value(key, value)

    click.echo(f"Successfully created a plot and saved into server with key={key}")


@usage.command()
@with_appcontext
def plot_ics_requests_hist():

    click.echo("Reading database...")
    df = md.table_to_dataframe(
        md.Usage, columns=["datetime", "url", "view_args", "path", "track_var"]
    )

    click.echo("Generating plot...")
    df = df[df.path.str.contains("calendar/schedule/link")]

    df["day"] = df.datetime.dt.floor("d")
    days = df.groupby("day")

    df = days.size()

    fig = go.Figure(
        go.Histogram(x=df.index, y=df.values, histfunc="sum", nbinsx=int(df.size))
    )
    fig.update_layout(
        title="iCalendar Requests",
        xaxis_title="Datetime",
        yaxis_title="Number of requests",
    )

    key = "[PLOT,context=usage]ics_requests_hist"
    server = app.config["MANAGER"].server
    value = fig.to_json()

    server.set_value(key, value)

    click.echo(f"Successfully created a plot and saved into server with key={key}")


@usage.command()
@with_appcontext
def plot_unique_ip_addresses_per_day():

    click.echo("Reading database...")
    df = md.table_to_dataframe(md.Usage, columns=["datetime", "remote_addr"])

    click.echo("Generating plot...")

    df["day"] = df.datetime.dt.floor("d")
    df = df.groupby("day").remote_addr.nunique()

    fig = go.Figure(
        go.Histogram(x=df.index, y=df.values, histfunc="sum", nbinsx=df.size)
    )

    fig.update_layout(
        title="Unique IP Addresses accessing ADE-Scheduler per day",
        xaxis_title="Datetime",
        yaxis_title="Number of unique IP addresses",
    )

    key = "[PLOT,context=usage]unique_ip_addresses_per_day"
    server = app.config["MANAGER"].server
    value = fig.to_json()

    server.set_value(key, value)

    click.echo(f"Successfully created a plot and saved into server with key={key}")
