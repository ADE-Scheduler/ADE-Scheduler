import click
import numpy as np
from flask.cli import with_appcontext

import backend.models as md


@click.group()
def schedules():
    """Performs operations with the schedules"""


@schedules.command()
@click.option(
    "-m", default=None, type=int, help="Number of most common codes, all by default."
)
@click.option(
    "-n", default=None, type=int, help="Number of most common prefixes, all by default."
)
@with_appcontext
def stats(m, n):
    """Returns some statistics about schedules."""
    schedules = md.Schedule.query.all()
    import re
    from collections import Counter

    c = Counter()
    prefixes = Counter()
    counts = []

    for schedule in schedules:
        counts.append(len(schedule.data.codes))
        c.update(schedule.data.codes)
        for code in schedule.data.codes:
            ma = re.search("^([A-Z]+)([0-9]+)", code)
            if ma is not None:
                prefixes[ma.group(1)] += 1

    click.echo("Most common codes:")
    for code, count in c.most_common(m):
        click.echo(f"\t{code:9s}: {count:4d}")

    click.echo("Most common code prefixes:")
    for prefix, count in prefixes.most_common(n):
        click.echo(f"\t{prefix:5s}: {count:5d}")

    counts = np.array(counts)

    click.echo(
        f"Average # of courses per schedule: {np.mean(counts):.1f} (std: {np.std(counts):.2f})"
    )
