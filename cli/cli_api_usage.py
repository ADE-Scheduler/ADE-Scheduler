import datetime

import click
import plotly.express as px
from flask import current_app as app
from flask.cli import with_appcontext

import backend.models as md


@click.group()
def api_usage():
    """Performs operations on the ApiUsage table."""
    pass


@api_usage.command()
@click.option(
    "--latest", default=-1, type=int, help="Only shows data from latest days."
)
@with_appcontext
def plot_requests_hist(latest):
    click.echo("Reading database...")

    table = md.ApiUsage

    sql_query = table.query

    if latest >= 0:
        sql_query = sql_query.filter(
            table.datetime >= datetime.datetime.now() - datetime.timedelta(days=latest)
        )

    sql_query = sql_query.with_entities(table.datetime, table.status)
    df = md.query_to_dataframe(sql_query)

    click.echo("Generating plot...")

    md.reformat_status_in_dataframe(df)
    df["day"] = df.datetime.dt.floor("d")
    df = df.groupby(["day", "status"]).size().to_frame()
    df.columns = ["count"]
    df.reset_index(level=0, inplace=True)
    df.reset_index(level=0, inplace=True)  # Do it twice here

    fig = px.histogram(df, x="day", y="count", color="status")

    fig.update_layout(
        title="ADE Api requests per status",
        xaxis_title="Datetime",
        yaxis_title="Number of requests",
        legend_title="Status",
    )

    key = "[PLOT,context=api_usage]requests_hist"
    server = app.config["MANAGER"].server
    value = fig.to_json()
    server.set_value(key, value)

    click.secho(
        f"Successfully created a plot and saved into server with key={key}", fg="green"
    )
