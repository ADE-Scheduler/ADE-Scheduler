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

    df["day"] = df.datetime.dt.floor("d")
    fig = px.histogram(df, x="day", color="blueprint")

    fig.update_layout(
        title="Requests per page per day",
        xaxis_title="Datetime",
        yaxis_title="Number of requests",
    )

    key = "[PLOT,context=usage]requests_per_blueprint_hist"
    server = app.config["MANAGER"].server
    value = fig.to_json()

    server.set_value(key, value)

    click.secho(
        f"Successfully created a plot and saved into server with key={key}", fg="green"
    )


@usage.command()
@with_appcontext
def plot_views_per_blueprint_hist():

    click.echo("Reading database...")
    df = md.table_to_dataframe(md.Usage, columns=["datetime", "blueprint", "path"])

    click.echo("Generating plot...")
    df.dropna(subset=["datetime", "blueprint"], inplace=True)

    index = np.logical_or.reduce(
        [df.path.str.endswith(f"/{blueprint}/") for blueprint in df.blueprint.unique()]
    )

    df = df[index]

    df["day"] = df.datetime.dt.floor("d")
    fig = px.histogram(df, x="day", color="blueprint")

    fig.update_layout(
        title="Views per page per day",
        xaxis_title="Datetime",
        yaxis_title="Number of views",
    )

    key = "[PLOT,context=usage]views_per_blueprint_hist"
    server = app.config["MANAGER"].server
    value = fig.to_json()

    server.set_value(key, value)

    click.secho(
        f"Successfully created a plot and saved into server with key={key}", fg="green"
    )


@usage.command()
@with_appcontext
def plot_ics_requests_hist():

    click.echo("Reading database...")
    df = md.table_to_dataframe(md.Usage, columns=["datetime", "view_args"])

    click.echo("Generating plot...")

    def view_args_to_link(view_args: dict):
        if "link" in view_args:
            return view_args
        else:
            return None

    df["link"] = df.view_args.apply(view_args_to_link)
    df.dropna(axis=0, subset=["link"], inplace=True)

    df["day"] = df.datetime.dt.floor("d")
    days = df.groupby("day")

    df = days.size()
    un = days.link.nunique()

    fig = go.Figure(
        go.Histogram(
            x=df.index, y=df.values, histfunc="sum", nbinsx=int(df.size), name="all"
        )
    )

    fig.add_trace(
        go.Histogram(
            x=un.index, y=un.values, histfunc="sum", nbinsx=int(un.size), name="unique"
        )
    )
    fig.update_layout(
        title="iCalendar downloads per day",
        xaxis_title="Datetime",
        yaxis_title="Number of downloads",
    )
    # Overlay both histograms
    fig.update_layout(barmode="overlay")
    # Reduce opacity to see both histograms
    fig.update_traces(opacity=0.75)

    key = "[PLOT,context=usage]ics_requests_hist"
    server = app.config["MANAGER"].server
    value = fig.to_json()

    server.set_value(key, value)

    click.secho(
        f"Successfully created a plot and saved into server with key={key}", fg="green"
    )


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
        title="Unique IP addresses accessing ADE-Scheduler per day",
        xaxis_title="Datetime",
        yaxis_title="Number of unique IP addresses",
    )

    key = "[PLOT,context=usage]unique_ip_addresses_per_day"
    server = app.config["MANAGER"].server
    value = fig.to_json()

    server.set_value(key, value)

    click.secho(
        f"Successfully created a plot and saved into server with key={key}", fg="green"
    )


@usage.command()
@with_appcontext
def plot_platforms_pie():

    click.echo("Reading database...")
    df = md.table_to_dataframe(md.Usage, columns=["ua_platform"])

    click.echo("Generating plot...")

    df.dropna(subset=["ua_platform"], inplace=True)

    fig = px.pie(df, names="ua_platform")

    fig.update_traces(textposition="inside", textinfo="percent+label")

    fig.update_layout(title="Distribution of usage per platform")

    key = "[PLOT,context=usage]platforms_pie"
    server = app.config["MANAGER"].server
    value = fig.to_json()

    server.set_value(key, value)

    click.secho(
        f"Successfully created a plot and saved into server with key={key}", fg="green"
    )
