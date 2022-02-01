from datetime import datetime
from multiprocessing.sharedctypes import Value

from flask import current_app as app
from flask import Blueprint, url_for, request, redirect, session, flash
from flask_login import login_user, logout_user
from flask_babel import gettext

import backend.models as md
import backend.cookies as cookies


security = Blueprint("security", __name__, static_folder="../static")


@security.route("/login")
def login():
    uclouvain = app.config["UCLOUVAIN_MANAGER"]

    # Request code
    if request.args.get("code") is None:
        redirect_uri = url_for("security.login", _external=True)
        return uclouvain.authorize_redirect(redirect_uri)

    # Code received
    else:
        # Fetch token
        token = uclouvain.authorize_access_token()

        # Fetch user role & ID
        my_fgs = None
        role = None
        resp = uclouvain.get("my/v0/digit/roles", token=token)
        if resp is None:
            flash(
                gettext(
                    "Hum... it looks like there is an issue with your UCLouvain account. Please contact directly so we can look into it and fix it for you ! Issue: base request"
                )
            )
            return redirect(url_for("calendar.index"))
        data = resp.json()

        roles = list()
        for business_role in data["businessRoles"]["businessRole"]:
            roles.append(business_role["businessRoleCode"])
            my_fgs = business_role["identityId"]

        # Determine which role, priority on employee, then student.
        if 1 in roles:
            role = "employee"
        elif 2 in roles:
            role = "student"
        else:
            flash(
                gettext(
                    "Hum... it looks like there is an issue with your UCLouvain account. Please contact directly so we can look into it and fix it for you ! Issue: role list"
                )
            )
            return redirect(url_for("calendar.index"))

        # Create user if does not exist
        user = md.User.query.filter_by(fgs=my_fgs).first()
        if user is None:
            resp = uclouvain.get(f"my/v0/{role}", token=token)
            if resp is None:
                flash(
                    gettext(
                        "Hum... it looks like there is an issue with your UCLouvain account. Please contact directly so we can look into it and fix it for you ! Issue: empty role"
                    )
                )
                return redirect(url_for("calendar.index"))
            data = resp.json()

            # Student
            if role == "student":
                data = data["lireDossierEtudiantResponse"]["return"]
                email = data["email"]
                first_name = data["prenom"]
                last_name = data["nom"]

            # Employee
            elif role == "employee":
                data = data["person"]
                email = data["email"]
                first_name = data["firstname"]
                last_name = data["lastname"]

            # Not implemented, raise error
            else:
                raise NotImplementedError(f"Role {role} is not implemented yet !")

            now = datetime.now()
            user = md.User(
                fgs=my_fgs,
                email=email,
                first_name=first_name,
                last_name=last_name,
                created_at=now,
                last_seen_at=now,
            )
            md.db.session.add(user)
            md.db.session.commit()

        # Login user
        login_user(user, remember=True)

        # Create response, redirect if next param is found
        next = session.pop("next", None)
        if next is not None:
            resp = redirect(next)
        else:
            resp = redirect(url_for("calendar.index"))
        return cookies.set_oauth_token(token, resp)


@security.route("/logout")
def logout():
    # Logout user
    logout_user()

    # Clear uclouvain token cookie
    resp = redirect(url_for("calendar.index"))
    resp.delete_cookie("uclouvain-token")
    return resp
