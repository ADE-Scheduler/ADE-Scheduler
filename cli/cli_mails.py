import json
import time

import click
import flask
from authlib.jose import jwt
from flask import current_app as app
from flask.cli import with_appcontext
from flask_mail import Message

import backend.models as md


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

        with (
            app.config["MAIL_MANAGER"].connect() as conn,
            click.progressbar(emails) as bar,
        ):
            for email in bar:
                time.sleep(2.5)  # Required for no-reply@uclouvain.be
                msg.recipients = [email]
                conn.send(msg)
    else:
        app.config["MAIL_MANAGER"].send(msg)


@mails.command()
@click.option("-d", "--dry-run", is_flag=True)
@click.option("-t", "--to-jyl-and-gerom", is_flag=True)
@with_appcontext
def send_jwt_token(dry_run, to_jyl_and_gerom):
    subject = "ADE Scheduler - Connexion avec l'identifiant UCLouvain"

    body = """
Bonjour à tous,

En moins d'un quadrimestre, le nombre d'utilisateurs inscrits sur notre site a plus de doublé, passant de 3000 à plus de 7000 ! Un énorme merci à vous ;-)
Au vu de ce succès, cela nous pousse encore plus à améliorer notre service.

Dès aujourd'hui, la connexion se fera via votre identifiant UCLouvain global. Tous les anciens comptes ont été désactivés. Cependant, vos abonnements iCal fonctionneront toujours et il vous sera possible de récupérer tous les calendriers associés à votre ancien compte. Pour cela, il vous suffit de cliquer sur le lien en fin de mail.

Cette transition vers le login UCLouvain nous permettra, dans un futur proche, d'automatiquement créer un horaire sur base de vos inscriptions aux cours, ainsi que d'avoir une synchronisation avec l'application UCLouvain (actuellement en développement). Pour les professeurs, un équivalent sera proposé avec les cours que vous donnez. Nous sommes d'ailleurs en discussion active pour améliorer d'autres services du site web, comme la carte des locaux.

Pour ceux qui ne le savent pas, nous avons tous les trois finis nos études et maintenir ADE Scheduler prend du temps. D'ailleurs, après plusieurs années de travail, Louis a décidé de quitter l'aventure pour se consacrer à d'autres projets, merci à lui !
Nous sommes donc à la recherche d'étudiants motivés ou curieux de nous aider à améliorer notre service, n'hésitez donc pas à nous contacter ;-)

Votre lien de récupération : {lien}.

Pour les étudiants, on espère que votre session et vos vacances se sont bien passées, et on vous souhaite une bonne rentrée !

Cordialement,

Gilles et Jérome.
    """
    msg = Message(subject=subject, body=body, recipients=[])

    emails = md.OldUser.get_emails()

    if to_jyl_and_gerom:
        emails = ["jeertmans@icloud.com", "gillesponcelet@skynet.be"]

    click.confirm(
        f"Are you sure to send an email to {len(emails)} email addresses?",
        abort=True,
    )

    with app.config["MAIL_MANAGER"].connect() as conn, click.progressbar(emails) as bar:
        for i, email in enumerate(bar):
            time.sleep(1.5)  # Required for no-reply@uclouvain.be

            msg.recipients = [email]

            payload = {"email": email}
            header = {"alg": "HS256"}
            token = jwt.encode(header, payload, app.config["SECRET_KEY"]).decode()
            msg.body = body.format(
                lien=f"https://ade-scheduler.info.ucl.ac.be/migrate/{token}"
            )
            if dry_run:
                click.echo(f"Sending message to {email}")
            else:
                conn.send(msg)
                click.echo(f"{i} - Sent a message to {email}")
