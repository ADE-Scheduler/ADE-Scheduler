# Python imports
import base64
import configparser
import distutils
import os
import traceback
import warnings
from datetime import timedelta

# External imports
import authlib.jose as jose
from authlib.integrations.flask_client import OAuth
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Flask imports
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from flask_babel import Babel, gettext
from flask_compress import Compress
from flask_jsglue import JSGlue
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    user_logged_in,
    user_logged_out,
)
from flask_mail import Mail, Message, email_dispatched
from flask_migrate import Migrate
from flask_session import Session

# External imports
from jsmin import jsmin
from lxml.etree import XMLSyntaxError
from requests.exceptions import ConnectionError, HTTPError
from werkzeug.exceptions import InternalServerError

# Backend imports
import backend.ade_api as ade
import backend.cookies as cookies
import backend.manager as mng
import backend.mixins as mxn
import backend.models as md
import backend.schedules as schd
import backend.security as scty
import backend.servers as srv
import backend.track_usage as tu
import backend.uclouvain_apis as ucl

# CLI commands
from cli import (
    cli_api_usage,
    cli_client,
    cli_external_calendars,
    cli_mails,
    cli_plots,
    cli_redis,
    cli_roles,
    cli_schedules,
    cli_sql,
    cli_usage,
    cli_users,
)

# Views imports
from views import utils as utl
from views.account import account
from views.admin import admin
from views.api import api
from views.calendar import calendar
from views.classroom import classroom
from views.contact import contact
from views.contribute import contribute
from views.help import help as _help
from views.security import security
from views.whatisnew import whatisnew

# Change current working directory to main directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))


# Setup app
app = Flask(__name__, template_folder="static/dist/html")

## Optionally enable profiling
app.config["PROFILE"] = (
    bool(distutils.util.strtobool(os.environ["PROFILE"]))
    if "PROFILE" in os.environ
    else False
)

if app.config["PROFILE"]:
    from werkzeug.middleware.profiler import ProfilerMiddleware

    profile_dir = "profile"
    if os.path.exists(profile_dir):
        if not os.path.isdir(profile_dir):
            warnings.warn(
                f"You cannot save the profiling to {profile_dir} since it is a file. It must be a directory."
            )
            profile_dir = None
    else:
        os.mkdir(profile_dir)
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir=profile_dir)

## Register blueprints
app.register_blueprint(security)
app.register_blueprint(calendar, url_prefix="/calendar")
app.register_blueprint(account, url_prefix="/account")
app.register_blueprint(classroom, url_prefix="/classroom")
app.register_blueprint(_help, url_prefix="/help")
app.register_blueprint(contact, url_prefix="/contact")
app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(whatisnew, url_prefix="/whatisnew")
app.register_blueprint(contribute, url_prefix="/contribute")
app.register_blueprint(admin, url_prefix="/admin")
app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]
app.config["SALT"] = os.environ["FLASK_SALT"]
jsglue = JSGlue(app)

# Register new commands
app.cli.add_command(cli_sql.sql)
app.cli.add_command(cli_redis.redis)
app.cli.add_command(cli_roles.roles)
app.cli.add_command(cli_client.client)
app.cli.add_command(cli_schedules.schedules)
app.cli.add_command(cli_usage.usage)
app.cli.add_command(cli_users.users)
app.cli.add_command(cli_api_usage.api_usage)
app.cli.add_command(cli_plots.plots)
app.cli.add_command(cli_mails.mails)
app.cli.add_command(cli_external_calendars.extcals)

# Load REDIS TTL config
redis_ttl_config = configparser.ConfigParser()
redis_ttl_config.read(".redis-config-ttl.cfg")
mode = os.environ["FLASK_ENV"]  # production of development

if mode not in redis_ttl_config:
    raise ValueError(f"Redis TTL config file is missing `{mode}` mode")

redis_ttl_config = srv.parse_redis_ttl_config(redis_ttl_config[mode])
app.config["REDIS_TTL"] = redis_ttl_config

# Setup the API Manager
app.config["ADE_API_CREDENTIALS"] = {
    "url": os.environ["ADE_URL"],
    "data": os.environ["ADE_DATA"],
    "Authorization": os.environ["ADE_AUTHORIZATION"],
}


app.config["ADE_FAKE_API"] = (
    bool(distutils.util.strtobool(os.environ["ADE_FAKE_API"]))
    if "ADE_FAKE_API" in os.environ
    else False
)

manager = mng.Manager(
    (
        ade.Client(app.config["ADE_API_CREDENTIALS"])
        if not app.config["ADE_FAKE_API"]
        else ade.FakeClient(app.config["ADE_API_CREDENTIALS"])
    ),
    srv.Server(host="localhost", port=6379),
    md.db,
    redis_ttl_config,
)
app.config["MANAGER"] = manager

# Setup Flask-Mail
app.config["MAIL_SERVER"] = os.environ["MAIL_SERVER"]
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ["MAIL_USERNAME"]
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", None)
app.config["MAIL_DEFAULT_SENDER"] = os.environ["MAIL_USERNAME"]
app.config["MAIL_MAX_EMAILS"] = (
    30  # Better for avoiding errors from no-reply@uclouvain.be
)
app.config["ADMINS"] = [os.environ["MAIL_ADMIN"]]

# Allows compression of text assets
# Production server has integrated compression support
if app.env == "development":
    compress = Compress(app)

for optional, default in [("MAIL_DISABLE", False), ("MAIL_SEND_ERRORS", True)]:
    if optional in os.environ:
        app.config[optional] = bool(distutils.util.strtobool(os.environ[optional]))
    else:
        app.config[optional] = default


def log_mail_message(message, app):
    """If mails are disabled, their content will be outputted in the debug output"""
    app.logger.debug(
        f"A mail was supposed to be send:\n"
        f"[SUBJECT]:\n{message.subject}\n"
        f"[BODY]:\n{message.body}\n"
        f"[END]"
    )


if app.config["MAIL_DISABLE"]:
    app.config["MAIL_DEBUG"] = True
    app.config["MAIL_SUPPRESS_SEND"] = True
    email_dispatched.connect(log_mail_message)


app.config["MAIL_MANAGER"] = Mail(app)

# Setup Flask-SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["ADE_DB_PATH"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
manager.database.init_app(app)
migrate = Migrate(app, manager.database)

# Setup Flask-Login
app.config["USE_SESSION_FOR_NEXT"] = True
login = LoginManager(app)
login.login_view = "security.login"
login.login_message = None
login.anonymous_user = mxn.AnonymousUser
app.config["LOGIN_MANAGER"] = login

# Setup UCLouvain OAuth2
oauth = OAuth(app, fetch_token=scty.fetch_token, update_token=scty.update_token)
oauth.register(
    # Client identification
    name="uclouvain",
    client_id=os.environ["UCLOUVAIN_CLIENT_ID"],
    client_secret=os.environ["UCLOUVAIN_CLIENT_SECRET"],
    api_base_url=ucl.API.BASE_URL,
    # Access token
    access_token_url=ucl.API.TOKEN_URL,
    access_token_params=None,
    # Authorization
    authorize_url=ucl.API.AUTHORIZE_URL,
    authorize_params=None,
)
app.config["UCLOUVAIN_MANAGER"] = oauth.create_client("uclouvain")

# Setup Flask-Session
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = manager.server
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(**redis_ttl_config["user_session"])
app.config["SESSION_MANAGER"] = Session(app)

# Setup Flask-Babel
app.config["LANGUAGES"] = ["en", "fr"]
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"
babel = Babel(app)


# Setup Fernet encryption / decryption
password = app.config["SECRET_KEY"].encode()
salt = app.config["SALT"].encode()
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=390000,
)
key = base64.urlsafe_b64encode(kdf.derive(password))
app.config["FERNET"] = Fernet(key)


# Jinja filter for autoversionning
@app.template_filter("autoversion")
def autoversion_filter(filename):
    fullpath = os.path.join("", filename[1:])
    try:
        timestamp = str(os.path.getmtime(fullpath))
    except OSError:
        return filename
    newfilename = "{0}?{1}".format(filename, timestamp)
    return newfilename


# Babel's locale "getter/setter"
@babel.localeselector
def get_locale():
    if session.get("locale") is None:
        session["locale"] = "fr"
    return session["locale"]


app.jinja_env.globals.update(get_locale=get_locale)


@app.route("/locale/<locale>")
def set_locale(locale):
    if locale in app.config["LANGUAGES"]:
        session["locale"] = locale
    return redirect(request.args.get("next"))


# Write jsglue.min.js
@app.before_first_request
def before_first_request():
    if not os.path.exists("static/dist"):
        os.makedirs("static/dist")
    with open("static/dist/jsglue.min.js", "w") as f:
        f.write(jsmin(jsglue.generate_js()))


@app.before_request
def before_request():
    tu.before_request()


@app.after_request
def after_request(response):
    # Check if a token has been refreshed
    token = g.pop("token", None)
    if token:
        response = cookies.set_oauth_token(token, response)
    return tu.after_request(response)


# Flask-Login's user loader
@login.user_loader
def load_user(fgs):
    return md.User.query.filter_by(fgs=fgs).first()


# Reset current schedule on user logout
@user_logged_out.connect_via(app)
def when_user_logged_out(sender, user):
    # When pressing confirmation link, somehow this function is triggered
    # without an initialised session...
    utl.init_session()

    if session["current_schedule"].id is not None:
        if (
            not user.is_anonymous
        ):  # Fixes problem whem confirmation link logs out but not account was actually logged in
            user.set_last_schedule_id(session["current_schedule"].id)

        session["current_schedule"] = schd.Schedule(manager.get_default_project_id())
        session["current_schedule_modified"] = False


# Load previous "current schedule" on user login
@user_logged_in.connect_via(app)
def when_user_logged_in(sender, user):
    if user.last_schedule_id is not None:
        if (
            session.get("current_schedule") is None
            or session["current_schedule"].is_empty()
        ):
            schedule = user.get_schedule(id=user.last_schedule_id)
            if schedule:
                session["current_schedule"] = schedule.data


# Main page
@app.route("/")
def welcome():
    if not session.get("previous_user"):
        utl.init_session()
        g.track_var["new user"] = "+1"
        session["previous_user"] = True
    return redirect(url_for("calendar.index"))


# Migration route
@app.route("/migrate/<token>")
@login_required
def migrate(token):
    # Decode token, fetch corresponding old user
    try:
        claims = jose.jwt.decode(token, app.config["SECRET_KEY"])
    except jose.errors.DecodeError:
        flash(
            gettext("Oops, it looks like you provided an invalid migration token."),
            "error",
        )
        return redirect(url_for("calendar.index"))
    email = claims["email"]
    old_user = md.OldUser.query.filter_by(email=email).first()
    if old_user is None or not old_user.is_active:
        flash(
            gettext(
                "Either this account does not exist or the data has already been migrated."
            ),
            "error",
        )
        return redirect(url_for("calendar.index"))

    # Add old user's schedules to current_user
    for s in old_user.schedules:
        current_user.schedules.append(s)

    # All done, deactivate old user
    old_user.confirmed_at = None
    md.db.session.commit()
    flash(
        gettext("Success: your data has been migrated to your new account !"), "success"
    )
    return redirect(url_for("calendar.index"))


# Error handlers
@app.errorhandler(HTTPError)
@app.errorhandler(ConnectionError)
def api_request_failed(e):
    """
    This catches the HTTPError raised when doing `resp.raise_for_status()`.
    Typically catches the ADE/UCLouvain API errors. This shouldn't be handled
    here, but acts as a failsafe in case we fail to do so elsewhere.

    These kind of failures are considered serious, thus we return a "website
    is down" page. (but could be improved/discussed)
    """
    return render_template("errorhandler/500.html", ade=True), 500


@app.errorhandler(XMLSyntaxError)
def handle_empty_ade_responses(e):
    """
    Sometimes (actually pretty often...) the API returns an empty response. Sigh.
    However, it does seem to resolve itself by trying again...
    In the meanwhile, flash an error message asking the user to try again.
    """
    err_text = gettext(
        "Hum... it looks like there's been a bug with the ADE API. Please try again and if the problem persists, do not hesitate to contact us !"
    )
    if request.accept_mimetypes.best == "application/json":
        return err_text, 500
    else:
        flash(err_text)
        return redirect(url_for("calendar.index")), 500


@app.errorhandler(InternalServerError)
def handle_exception(e):
    if not app.debug and app.config["MAIL_SEND_ERRORS"]:
        error = e.original_exception
        error_request = f"{request.path} [{request.method}]"
        error_module = error.__class__.__module__
        if error_module is None:
            error_name = error.__class__.__name__
        else:
            error_name = f"{error_module}.{error.__class__.__name__}"
        error_details = str(traceback.format_exc())
        msg = Message(
            subject=f"ADE Scheduler Failure: {error_name}",
            body=f"Exception on {error_request}: {str(error)}\n\n{error_details}",
            recipients=app.config["ADMINS"],
        )
        app.config["MAIL_MANAGER"].send(msg)

    if request.accept_mimetypes.best == "application/json":
        return gettext("An unknown error has occurred"), 500
    else:
        return render_template("errorhandler/500.html"), 500


@app.errorhandler(403)  # FORBIDDEN
def forbidden(e):
    if request.accept_mimetypes.best == "application/json":
        return gettext("Access to this resource is forbidden."), e.code
    else:
        return (
            render_template(
                "errorhandler/403.html", message="403 Forbidden access ヽ(ಠ_ಠ) ノ"
            ),
            e.code,
        )


@app.errorhandler(404)  # URL NOT FOUND
@app.errorhandler(405)  # METHOD NOT ALLOWED
def page_not_found(e):
    if request.accept_mimetypes.best == "application/json":
        return gettext("Resource not found"), e.code
    else:
        return (
            render_template(
                "errorhandler/404.html", message=gettext("404 Page not found :(")
            ),
            e.code,
        )


# Shell context default exports
@app.shell_context_processor
def make_shell_context():
    return {
        "db": md.db,
        "Role": md.Role,
        "Schedule": md.Schedule,
        "Link": md.Link,
        "User": md.User,
        "oUser": md.OldUser,
        "Role": md.Role,
        "Usage": md.Usage,
        "Api": md.ApiUsage,
        "mng": app.config["MANAGER"],
    }
