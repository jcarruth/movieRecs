""" Manages connection to a mongoDb database """

from pymongo import MongoClient
from pymongo.database import Database

from flask import Flask, current_app, g


def get_db() -> Database:
    """Provides access to the database"""

    if "db" not in g:
        username = current_app.config["DB_USER"]
        password = current_app.config["DB_PASSWORD"]
        host = current_app.config["DB_HOST"]
        port = current_app.config["DB_PORT"]
        uri = f"mongodb://{username}:{password}@{host}:{port}"
        client = MongoClient(uri)
        g.db = client[current_app.config["DB_NAME"]]

    return g.db


def close_db(e=None):
    """ Closes the database connection """
    db: Database = g.pop("db", None)

    if db is not None:
        db.client.close()


def clear_db():
    """ Clear all collections from database """
    db = get_db()

    for collection in db.list_collection_names():
        db.drop_collection(collection)


def add_movie(movie_data: dict):
    """ Adds a single movie to the database """
    db = get_db()
    movie_collection = db.movies
    movie_collection.insert_one(movie_data)


def init_app(app: Flask):
    """ Register any necessary methods with the app """
    app.teardown_appcontext(close_db)
