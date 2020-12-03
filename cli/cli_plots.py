import click
from cli.cli_api_usage import plot_requests_hist
from cli.cli_users import plot_users_hist, plot_users_emails_pie
from cli.cli_usage import plot_requests_per_blueprint_hist

F_PLOTS = {
    "api-usage-requests-hist": plot_requests_hist,
    "requests-per-blueprint-hist": plot_requests_per_blueprint_hist,
    "users-hist": plot_users_hist,
    "users-emails-pie": plot_users_emails_pie
}


@click.group()
def plots():
    """Performs operations with Plotly backend"""
    pass


@plots.command()
@click.option(
    "-s",
    "--select",
    type=click.Choice(["all"] + list(F_PLOTS.keys()), case_sensitive=False),
    default="all",
    help="Generate a plot for a given function. By default, will generate all plots."
)
@click.pass_context
def generate(ctx, select):
    if select == "all":
        for key, f in F_PLOTS.items():
            click.secho(f"Generating plot: {key}")
            ctx.invoke(f)
    else:
        f = F_PLOTS[select]
        ctx.invoke(f)

