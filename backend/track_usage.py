from datetime import datetime

from flask import request, g
from flask_security import current_user

import backend.models as md


def before_request():
    g.start_time = datetime.utcnow()
    g.track_var = dict()


def after_request(response):
    end_time = datetime.utcnow()
    speed = end_time - g.start_time

    md.Usage(
        dict(
            url=request.url,
            status=response.status_code,
            username=current_user.email if current_user.is_authenticated else None,
            user_agent=request.user_agent,
            blueprint=request.blueprint,
            path=request.path,
            endpoint=request.endpoint,
            view_args=request.view_args,
            url_args=dict([(k, request.args[k]) for k in request.args]),
            datetime=end_time,
            speed=speed.total_seconds(),
            remote_addr=request.remote_addr,
            track_var=g.track_var,
        )
    )

    return response
