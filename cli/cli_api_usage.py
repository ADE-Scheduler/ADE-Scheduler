import click
import backend.models as md

import plotly.express as px

from flask import current_app as app
from flask.cli import with_appcontext


@click.group()
def api_usage():
    """Performs operations on the ApiUsage table."""
    pass


@api_usage.command()
@with_appcontext
def plot_requests_hist():

    click.echo("Reading database...")
    df = md.table_to_dataframe(md.ApiUsage, columns=["status", "datetime"])

    click.echo("Generating plot...")

    md.reformat_status_in_dataframe(df)
    df["day"] = df.datetime.dt.floor("d")
    fig = px.histogram(df, x="day", color="status", nbins=100)

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
