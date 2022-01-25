from datetime import datetime

from flask import current_app as app
from flask import Blueprint, url_for, request, redirect, session
from flask_login import login_user, logout_user

import backend.models as md
import backends.cookies as cookies


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
        resp = redirect(url_for("calendar.index"))
        resp = cookies.set_oauth_token(token, resp)

        # Fetch user role & ID
        my_fgs = None
        role = None
        data = uclouvain.get("my/v0/digit/roles", token=token).json()

        roles = list()
        for business_role in data["businessRoles"]["businessRole"]:
            roles.append(business_role["businessRoleCode"])
            # The FGS *should* be the unique identifier TODO: check this ?
            my_fgs = business_role["identityId"]

        # Determine which role, priority on employee, then student.
        if 1 in roles or 13 in roles:  # TODO: check what does the 13 correspond to
            # I think it is the "Boursier UCL" role
            # We shoud also ask a list of existing roles...
            role = "employee"
        elif 2 in roles:
            role = "student"
        else:
            raise NotImplementedError(
                f"This dude is neither a student or an employee: {roles}"
            )

        # Create user if does not exist
        user = md.User.query.filter_by(fgs=my_fgs).first()
        if user is None:
            data = uclouvain.get(f"my/v0/{role}", token=token).json()

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

        # User already exists, nothing to do
        else:
            pass

        # Login user
        login_user(user)
        next = session.pop("next", None)
        if next is not None:
            return redirect(next)


        return resp


@security.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("calendar.index"))
