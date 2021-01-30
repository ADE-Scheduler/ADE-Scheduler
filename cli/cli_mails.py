import click
import backend.models as md

from flask import current_app as app
from flask_mail import Message
from flask.cli import with_appcontext
import flask

import json


@click.group()
def mails():
    """Performs operations with e-mails."""
    pass


@mails.command()
@click.option("-s", "--subject", default="", type=str, help="Subject")
@click.option("-b", "--body", default="", type=str, help="Body")
@click.option("-r", "--recipients", default=[""], type=list, help="List of recipients")
@click.option(
    "-f",
    "--filename",
    default="",
    type=click.Path(),
    help="If present, will retrieve message information from JSON file",
)
@click.option("-u", "--all-users", is_flag=True)
@with_appcontext
def send(subject, body, recipients, filename, all_users):

    if filename:
        with open(filename) as f:
            content = json.load(f)
            subject = content["subject"]
            body = content["body"]
            recipients = content["recipients"]

    msg = Message(subject=subject, body=body, recipients=recipients)

    if all_users:
        df = md.table_to_dataframe(md.User, columns=["confirmed_at", "email"])
        df.dropna(subset=["confirmed_at"], inplace=True)

        # We do not want tu publicly share email adresses so we use BCC
        msg.recipients = []
        msg.bcc = df.email.values.tolist()

    app.config["MAIL_MANAGER"].send(msg)
