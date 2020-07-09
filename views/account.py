from flask import Blueprint, render_template, session
from flask_security import login_required


account = Blueprint('account', __name__, static_folder='../static')

@account.route('/')
@login_required
def dashboard():
    return render_template('account.html')
