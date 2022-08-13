import click
from flask.cli import with_appcontext

import backend.models as md


@click.group()
def extcals():
    """Performs actions on external calendars."""


@extcals.command()
@with_appcontext
def list():
    """Lists external calendars."""
    for ec in md.ExternalCalendar.query.all():
        click.echo(
            f"{ec.id:3d} - approved: {str(ec.approved).lower()} - {ec.code:20s} - {ec.name}"
        )


@extcals.command()
@click.argument("ids", type=int, nargs=-1)
@with_appcontext
def get(ids):
    """Returns link of external calendar with given ids."""
    ecs = md.ExternalCalendar.query.filter(md.ExternalCalendar.id.in_(ids)).all()

    for ec in ecs:
        click.echo(ec.url)


@extcals.command()
@click.argument("ids", type=int, nargs=-1)
@with_appcontext
def delete(ids):
    """Deletes external calendars with given ids."""
    md.ExternalCalendar.query.filter(md.ExternalCalendar.id.in_(ids)).delete()
    md.db.session.commit()


@extcals.command()
@click.argument("ids", type=int, nargs=-1)
@with_appcontext
def approve(ids):
    """Approves external calendars with given ids."""
    md.ExternalCalendar.query.where(md.ExternalCalendar.id.in_(ids)).update(
        values=dict(approved=True)
    )
    md.db.session.commit()


@extcals.command()
@click.argument("ids", type=int, nargs=-1)
@with_appcontext
def disapprove(ids):
    """Disapproves external calendars with given ids."""
    md.ExternalCalendar.query.where(md.ExternalCalendar.id.in_(ids)).update(
        values=dict(approved=False)
    )
    md.db.session.commit()
