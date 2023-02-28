import datetime
import json

import click
import flask
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask import current_app as app
from flask.cli import with_appcontext

import backend.models as md


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
@click.option(
    "--latest", default=-1, type=int, help="Only shows data from latest days."
)
@with_appcontext
def plot_requests_per_blueprint_hist(latest):
    click.echo("Reading database...")

    table = md.Usage

    sql_query = table.query

    if latest >= 0:
        sql_query = sql_query.filter(
            table.datetime >= datetime.datetime.now() - datetime.timedelta(days=latest)
        )

    sql_query = sql_query.with_entities(table.datetime, table.blueprint)
    df = md.query_to_dataframe(sql_query)

    click.echo("Generating plot...")
    df.dropna(subset=["datetime", "blueprint"], inplace=True)

    df["day"] = df.datetime.dt.floor("d")
    df = df.groupby(["day", "blueprint"]).size().to_frame()
    df.columns = ["count"]
    df.reset_index(level=0, inplace=True)
    df.reset_index(level=0, inplace=True)

    fig = px.histogram(df, x="day", y="count", color="blueprint")

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
@click.option(
    "--latest", default=-1, type=int, help="Only shows data from latest days."
)
@with_appcontext
def plot_views_per_blueprint_hist(latest):
    click.echo("Reading database...")
    table = md.Usage

    sql_query = table.query

    if latest >= 0:
        sql_query = sql_query.filter(
            table.datetime >= datetime.datetime.now() - datetime.timedelta(days=latest)
        )

    sql_query = sql_query.with_entities(table.datetime, table.blueprint, table.path)
    df = md.query_to_dataframe(sql_query)

    click.echo("Generating plot...")
    df.dropna(subset=["datetime", "blueprint"], inplace=True)

    index = np.logical_or.reduce(
        [df.path.str.endswith(f"/{blueprint}/") for blueprint in df.blueprint.unique()]
    )

    df = df[index]

    df["day"] = df.datetime.dt.floor("d")
    df = df.groupby(["day", "blueprint"]).size().to_frame()
    df.columns = ["count"]
    df.reset_index(level=0, inplace=True)
    df.reset_index(level=0, inplace=True)

    fig = px.histogram(df, x="day", y="count", color="blueprint")

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
    df = md.table_to_dataframe(md.Usage, columns=["datetime", "url_args"])

    click.echo("Generating plot...")

    def url_args_to_link(url_args: str):
        if url_args:
            try:
                url_args: dict = json.loads(url_args)
                return url_args.get("link", None)
            except json.JSONDecodeError:
                # This error is caused by too long `url_args` values
                # that might have been truncated
                # After testing, this only seems to by caused by url attacks
                return None

        return None

    df["link"] = df.url_args.apply(url_args_to_link)
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
    sql_query = md.Usage.query.with_entities(md.Usage.ua_platform)
    df = md.query_to_dataframe(sql_query)

    click.echo("Generating plot...")

    df["ua_platform"] = df["ua_platform"].str.lower()
    df = df.groupby("ua_platform").size().to_frame()
    df.columns = ["count"]
    df.reset_index(level=0, inplace=True)

    fig = px.pie(df, values="count", names="ua_platform")

    fig.update_traces(textposition="inside", textinfo="percent+label")

    fig.update_layout(title="Distribution of usage per platform")

    key = "[PLOT,context=usage]platforms_pie"
    server = app.config["MANAGER"].server
    value = fig.to_json()

    server.set_value(key, value)

    click.secho(
        f"Successfully created a plot and saved into server with key={key}", fg="green"
    )
