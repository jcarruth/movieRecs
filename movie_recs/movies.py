""" Provides a blueprint with routes and views for movies """

from flask import Blueprint, flash, redirect, render_template, request, url_for
from pymongo.errors import DuplicateKeyError

from .auth import login_required
from .db import add_movie, get_movie_by_slug, get_movies
from .omdb import get_movie_data

bp = Blueprint("movies", __name__)


@bp.route("/")
def list_movies():
    """ Provide view of all movies"""
    movies = get_movies()

    return render_template("movies/list.html", movies=movies)


@bp.route("/movie/<string:slug>")
def movie_details(slug: str):
    """ Provide view for a single movie """
    movie = get_movie_by_slug(slug)

    return render_template("movies/movie.html", movie=movie)


@bp.route("/movies/add", methods=("GET", "POST"))
@login_required
def add():
    """ Log a user in """
    movie_title = ""
    if request.method == "POST":
        movie_title = request.form["movie_title"]

        error = None

        if not movie_title:
            error = "A movie title is required"

        if error is None:
            try:
                movie_data = get_movie_data(movie_title)
            except LookupError:
                error = f"The movie \"{movie_title}\" was not found in the OMDB."

        if error is None:
            try:
                add_movie(movie_data)
            except DuplicateKeyError:
                error = f"The movie \"{movie_title}\" has already been added."

        if error is None:
            return redirect(url_for("movies.movie_details", slug=movie_data["slug"]))

        flash(error)

    return render_template("movies/add.html", movie_title=movie_title)
