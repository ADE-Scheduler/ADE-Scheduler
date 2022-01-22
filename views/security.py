from flask import current_app as app
from flask import Blueprint, url_for, request, redirect
from flask_login import login_user, logout_user

import backend.models as md


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
        data = uclouvain.get("my/v0/digit/roles", token=token).json()
        for business_role in data["businessRoles"]["businessRole"]:
            if business_role["businessRoleCode"] == 1:
                role = "student"
                my_fgs = business_role["identityId"]
            elif business_role["businessRoleCode"] == 2:
                role = "employee"
                my_fgs = business_role["identityId"]

        # Create user if does not exist
        user = md.User.query.filter_by(fgs=my_fgs).first()
        if user is None:
            data = uclouvain.get(f"my/v0/{role}", token=token).json()
            email = data["person"]["email"]
            first_name = (
                data["person"]["firstname"]
                if role == "employee"
                else data["person"]["prenom"]
            )
            last_name = (
                data["person"]["lastname"]
                if role == "employee"
                else data["person"]["nom"]
            )
            # TODO: vérifier que c'est bon pour le role student...
            user = md.User(
                fgs=my_fgs,
                email=email,
                first_name=first_name,
                last_name=last_name,
                token=md.OAuth2Token("uclouvain", token),
            )
            md.db.session.add(user)
            md.db.session.commit()

        # User already exists, update token
        else:
            user.token.update(token)

        # Login user
        login_user(user)
        return redirect(url_for("calendar.index"))


@security.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("calendar.index"))
