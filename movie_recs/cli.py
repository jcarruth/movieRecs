""" Sets up command line commands"""
import click
from flask import Flask
from flask.cli import with_appcontext

from .db import clear_db, init_collections, add_movie
from .movie_list import top_100_classic_movies
from .omdb import get_movie_data


def init_db():
    """ Clear all collections from the database, then add classic movies"""
    clear_db()
    init_collections()

    # Add all top 100 classic movies to the database
    for movie_title in top_100_classic_movies:
        movie_data = get_movie_data(movie_title)
        add_movie(movie_data)


@click.command("init-db")
@with_appcontext
def init_db_command():
    """ CLI command to initialize database """
    init_db()
    click.echo("Initialized the database")


def add_cli_commands(app: Flask):
    """ Add all cli commands to app """
    app.cli.add_command(init_db_command)
