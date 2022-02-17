from datetime import datetime

from flask import g, request
from flask_login import current_user
from ua_parser import user_agent_parser
from werkzeug.user_agent import UserAgent
from werkzeug.utils import cached_property

import backend.models as md


class ParsedUserAgent(UserAgent):
    @cached_property
    def _details(self):
        return user_agent_parser.Parse(self.string)

    @property
    def platform(self):
        return self._details["os"]["family"]

    @property
    def browser(self):
        return self._details["user_agent"]["family"]

    @property
    def version(self):
        ua = self._details["user_agent"]
        return ".".join(
            ua[key] for key in ("major", "minor", "patch") if ua[key] is not None
        )


def before_request():
    g.start_time = datetime.utcnow()
    g.track_var = dict()


def after_request(response):
    if current_user.is_authenticated:
        current_user.last_seen_at = datetime.now()
        # Session will be commited after the new usage line is added,
        # no need to do it here.

    end_time = datetime.utcnow()
    speed = end_time - g.start_time

    md.Usage(
        dict(
            url=request.url,
            status=response.status_code,
            username=current_user.email if current_user.is_authenticated else None,
            user_agent=ParsedUserAgent(request.user_agent.string),
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
