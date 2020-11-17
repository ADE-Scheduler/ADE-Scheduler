import click
import numpy as np

from flask.cli import with_appcontext

import backend.models as md


@click.group()
def schedules():
    """Performs operations with the schedules"""


@schedules.command()
@click.option(
    "-n", default=None, type=int, help="Number of most common codes, all by default."
)
@with_appcontext
def stats(n):
    """Returns some statistics about schedules."""
    schedules = md.Schedule.query.all()
    from collections import Counter
    import re

    c = Counter()
    prefixes = Counter()
    counts = []

    for schedule in schedules:
        counts.append(len(schedule.data.codes))
        c.update(schedule.data.codes)
        for code in schedule.data.codes:
            m = re.search("^([A-Z]+)([0-9]+)", code)
            if m is not None:
                prefixes[m.group(1)] += 1

    click.echo("Most common codes:")
    for code, count in c.most_common(n):
        click.echo(f"\t{code}: {count}")

    click.echo("Most common code prefixes:")
    for prefix, count in prefixes.most_common():
        click.echo(f"\t{prefix}: {count}")

    counts = np.array(counts)

    click.echo(
        f"Average # of courses per schedule: {np.mean(counts):.1f} (std: {np.std(counts):.2f})"
    )
