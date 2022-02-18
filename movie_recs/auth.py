""" Provides authentication blueprint """
import functools

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from pymongo.errors import DuplicateKeyError
from werkzeug.security import check_password_hash, generate_password_hash

from .db import add_user, get_user_by_id, get_user_by_username

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    """ Attempt to register a new user """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        error = None

        if not username:
            error = "Username is required"
        elif not password:
            error = "Password is required"

        if error is None:
            password_hash = generate_password_hash(password)
            try:
                add_user(username, password_hash)
            except DuplicateKeyError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """ Log a user in """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        error = None

        user = get_user_by_username(username)

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password_hash"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["_id"]

            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """ Log the current user out """
    session.clear()
    return redirect(url_for("index"))


@bp.before_app_request
def load_logged_in_user():
    """ Add user data to g for the currently logged in user """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_user_by_id(user_id)


def login_required(view):
    """ Decorator for view functions that will require login """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
