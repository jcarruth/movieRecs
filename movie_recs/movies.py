""" Provides a blueprint with routes and views for movies """

from flask import Blueprint, render_template

from .db import get_movies, get_movie_by_slug

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
