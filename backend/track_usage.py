from datetime import datetime

from flask import request, g
from flask_security import current_user


def before_request():
    g.start_time = datetime.utcnow()


def after_request(response):
    endpoint = request.endpoint
    path = request.path
    method = request.method
    user_agent = request.user_agent
    args = dict(**request.args, **request.view_args)
    # This combines view_args & url_args
    # Should we save the payload of POST request ? (e.g for calendar.udpate_color)
    time = datetime.utcnow()
    speed = time - g.start_time
    username = current_user.email if current_user.is_authenticated else None
    status_code = request.status_code

    print("\nDoing process before request...")
    print(f"Endpoint   : {endpoint}")
    print(f"Path       : {path}")
    print(f"Method     : {method}")
    print(f"User agent : {user_agent}")
    print(f"Args       : {args}")
    print(f"Time       : {time}")
    print(f"Speed      : {speed.total_seconds()}")
    print(f"Username   : {username}")
    print(f"Status code: {status_code}")

    print("Process done !\n")
