import click
from flask.cli import with_appcontext

import backend.models as md


@click.group()
def roles():
    """Manage roles"""


@roles.command()
@click.option(
    "-n",
    "--name",
    help="Name of the role",
)
@click.option(
    "-d",
    "--description",
    help="Description of the role",
)
@with_appcontext
def create(name, description):
    role = md.Role(name=name, description=description)
    md.db.session.add(role)
    md.db.session.commit()


@roles.command()
@click.option("-e", "--email", help="User's email")
@click.option("-r", "--role", help="Role to add")
@with_appcontext
def add(email, role):
    user = md.User.query.filter_by(email=email).first()
    user.add_role(role)
