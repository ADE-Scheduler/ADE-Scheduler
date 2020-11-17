import click
import backend.models as md

import plotly.graph_objects as go
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
    colors = px.colors.qualitative.Plotly
    fig = go.Figure()

    click.echo("Reading datase...")
    df = md.table_to_dataframe(md.ApiUsage)

    click.echo("Generating plot...")
    figs = df.groupby("status").datetime.hist(bins=100, legend=True, backend="plotly")

    i = 0
    for figure in figs:
        for trace in figure.select_traces():
            trace.marker.color = colors[i]
            fig.add_trace(trace)

            i += 1

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

    click.echo(f"Successfully created a plot and saved into server with key={key}")
