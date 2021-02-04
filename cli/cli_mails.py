import click
import time
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
    type=click.Path(exists=True),
    help="If present, will retrieve message information from JSON file",
)
@click.option(
    "-h",
    "--html",
    default="",
    type=click.Path(exists=True),
    help="If present, will retrieve html information from HTML file",
)
@click.option("-u", "--all-users", is_flag=True)
@with_appcontext
def send(subject, body, recipients, filename, html, all_users):

    if filename:
        with open(filename) as f:
            content = json.load(f)
            msg = Message(**content)
    else:
        msg = Message(subject=subject, body=body, recipients=recipients)

    if html:
        with open(html) as f:
            msg.html = f.read()

    if all_users:
        emails = md.User.get_emails()

        click.confirm(
            f"Are you sure to send an email to {len(emails)} email addresses?",
            abort=True,
        )

        with app.config["MAIL_MANAGER"].connect() as conn, click.progressbar(
            emails
        ) as bar:
            for email in bar:
                time.sleep(2.5)  # Required for no-reply@uclouvain.be
                msg.recipients = [email]
                conn.send(msg)
    else:
        app.config["MAIL_MANAGER"].send(msg)
