import click
import pandas as pd
from datetime import datetime

from flask import current_app as app
from flask.cli import with_appcontext
from flask_security.cli import users

import plotly.express as px
from plotly.subplots import make_subplots

import backend.models as md


@users.command()
@with_appcontext
def count():
    """Count the number of current users."""
    click.echo(
        f"There are currently {md.User.query.filter(None != md.User.confirmed_at).count()} "
        f"(confirmed) users on ADE-Scheduler."
    )


@users.command()
@with_appcontext
def stats():
    """Returns some statistics about users."""
    confirmed_users = md.User.query.filter(None != md.User.confirmed_at).all()
    df = pd.DataFrame(
        [
            [user.confirmed_at.strftime("%Y/%m/%d"), user.email, len(user.schedules)]
            for user in confirmed_users
        ],
        columns=["date", "email", "n_schedules"],
    )

    click.echo("Accounts created per day:")
    for date, count in df.groupby("date").size().iteritems():
        click.echo(f"\t{date}: {count}")
    click.echo(f"\tTotal: {len(confirmed_users)}")

    click.echo("Email domains:")

    df["email"] = df["email"].apply(lambda s: s.split("@")[1])

    for domain, count in df.groupby("email").size().iteritems():
        click.echo(f"\t{domain}: {count}")

    click.echo("Schedules count stats:")
    description = df["n_schedules"].describe()
    description["count"] = df["n_schedules"].sum()
    for x, value in description.iteritems():
        click.echo(f"\t{x}: {value}")


@users.command()
@with_appcontext
def plot_users_hist():

    colors = px.colors.qualitative.Plotly

    click.echo("Reading database...")
    df = md.table_to_dataframe(md.User, columns=["confirmed_at"])
    df.dropna(subset=["confirmed_at"], inplace=True)
    df.confirmed_at = df.confirmed_at.dt.floor("d")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    click.echo("Generating plot...")
    fig_1 = df.confirmed_at.hist(bins=100, backend="plotly")
    fig_2 = df.confirmed_at.hist(bins=100, cumulative=True, backend="plotly")

    trace_1 = next(fig_1.select_traces())
    trace_1.name = "per datetime"
    trace_1.marker.color = colors[0]
    fig.add_trace(trace_1, secondary_y=False)

    trace_2 = next(fig_2.select_traces())
    trace_2.name = "cumulative"
    trace_2.marker.color = colors[1]
    trace_2.opacity = 0.5
    fig.add_trace(trace_2, secondary_y=True)

    fig.update_layout(
        title="Number of users created per datetime",
        xaxis_title="Datetime",
        yaxis_title="Number of users",
    )

    key = "[PLOT,context=users]users_hist"
    server = app.config["MANAGER"].server
    value = fig.to_json()
    server.set_value(key, value)

    click.secho(
        f"Successfully created a plot and saved into server with key={key}", fg="green"
    )


@users.command()
@with_appcontext
def plot_users_emails_pie():

    click.echo("Reading datase...")
    df = md.table_to_dataframe(md.User, columns=["confirmed_at", "email"])
    df.dropna(subset=["confirmed_at"], inplace=True)

    df["count"] = 1
    df["email"] = df["email"].apply(lambda s: s.split("@")[1])

    fig = px.pie(df, values="count", names="email")

    fig.update_layout(title="Repartition of accounts across email domains")
    fig.update_traces(textposition="inside")
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode="hide")

    key = "[PLOT,context=users]users_emails_pie"
    server = app.config["MANAGER"].server
    value = fig.to_json()
    server.set_value(key, value)

    click.secho(
        f"Successfully created a plot and saved into server with key={key}", fg="green"
    )
