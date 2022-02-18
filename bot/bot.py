import json
import os
import subprocess

import dotenv
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler, Updater

# Relevant IDs
dotenv.load_dotenv(".botenv")
gop_id = int(os.environ["GOP_ID"])
admins = json.loads(os.environ["ADMIN_ID"])

# Service list
services = ["httpd", "redis", "postgresql"]


def admin_required(func):
    def wrapper(update: Update, context: CallbackContext):
        user_id = update.message.from_user.id

        if user_id not in admins:
            fname = update.message.from_user.first_name
            lname = update.message.from_user.last_name
            update.message.reply_text(
                f"{fname} {lname}, you are a sneaky lil' bastard !"
            )
        else:
            func(update, context)

    return wrapper


@admin_required
def service_command(update: Update, context: CallbackContext):
    """
    Interact with the server's services: Redis, PostgreSQL & Apache.
    """

    commands = ["start", "stop", "reload", "restart"]

    # Load args
    try:
        command = context.args[0]
        service = context.args[1]

        if command not in commands:
            update.message.reply_text("Unknown command !")
            return

        if service not in services:
            update.message.reply_text("Unknown service !")
            return

    except (IndexError, ValueError):
        update.message.reply_text("Please specify a command and a service.")
        return

    # Execute command
    subprocess.call(["systemctl", command, service])
    update.message.reply_text(f"{command} {service} successful !")


@admin_required
def status_command(update: Update, context: CallbackContext):
    """
    Display service status.
    """

    for service in services:
        res = subprocess.run(
            ["systemctl", "status", service],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if res.stdout:
            update.message.reply_markdown_v2(f"```\n{res.stdout.decode()}\n```")
        if res.stderr:
            update.message.reply_markdown_v2(f"```\n{res.stderr.decode()}\n```")


@admin_required
def top_command(update: Update, context: CallbackContext):
    """
    Display processes usage using top tool.
    """
    commands = ["mem", "cpu"]

    # Load args
    try:
        command = context.args[0]

        if command not in commands:
            update.message.reply_text("Unknown command !")
            return

    except (IndexError, ValueError):
        command = "mem"

    res = subprocess.run(
        ["ps", "-o", "%cpu,%mem,comm", "ax", f"--sort=-%{command}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    res = subprocess.run(
        ["head", "-20"],
        input=res.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if res.stdout:
        update.message.reply_markdown_v2(f"```\n{res.stdout.decode()}\n```")
    if res.stderr:
        update.message.reply_markdown_v2(f"```\n{res.stderr.decode()}\n```")


@admin_required
def flask_command(update: Update, context: CallbackContext):
    """
    Interact with the Flask CLI.
    """

    # flask run should NOT be called
    if context.args[0] == "run":
        update.message.reply_text("Bad idea...")
        return

    res = subprocess.run(
        ["venv/bin/flask"] + context.args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if res.stdout:
        update.message.reply_markdown_v2(f"```\n{res.stdout.decode()}\n```")
    if res.stderr:
        update.message.reply_markdown_v2(f"```\n{res.stderr.decode()}\n```")


def health_check(context: CallbackContext):
    """
    Periodic job to check the services' status.
    """

    # Check services status
    for service in services:
        try:
            subprocess.check_call(
                ["systemctl", "status", service],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError:
            context.bot.send_message(
                chat_id=gop_id,
                text=f"{service} is down ! Please run `/service restart {service}`",
                parse_mode=ParseMode.MARKDOWN,
            )


# Updater object
updater = Updater(os.environ["BOT_KEY"], use_context=True)

# Dispatcher & Job Queue
dispatcher = updater.dispatcher
job_queue = updater.job_queue

# Commands
dispatcher.add_handler(CommandHandler("service", service_command))
dispatcher.add_handler(CommandHandler("status", status_command))
dispatcher.add_handler(CommandHandler("flask", flask_command))
dispatcher.add_handler(CommandHandler("top", top_command))

# Repeating tasks
job_queue.run_repeating(health_check, interval=60, first=10)

# Start bot
updater.start_polling()
updater.idle()
