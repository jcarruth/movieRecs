""" Manages connection to a mongoDb database """

from cgitb import lookup
from pymongo import MongoClient
from bson.objectid import ObjectId
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


def init_collections():
    """ Set up collections in database with indices """
    db = get_db()

    db.movies.create_index("slug", unique=True)
    db.users.create_index("username", unique=True)


def add_movie(movie_data: dict):
    """ Adds a single movie to the database """
    db = get_db()
    movie_collection = db.movies
    movie_collection.insert_one(movie_data)


def add_user(username: str, password_hash: str):
    """ Add a user to the database """

    db = get_db()
    user_data = {
        "username": username,
        "password_hash": password_hash,
    }
    db.users.insert_one(user_data)


def get_user_by_username(username: str):
    """ Look up a user using their username """
    db = get_db()

    user = db.users.find_one({"username": username})
    user["_id"] = str(user["_id"])

    return user


def get_user_by_id(user_id: str):
    """ Look up a user using their id """
    db = get_db()

    user = db.users.find_one({"_id": ObjectId(user_id)})
    user["_id"] = str(user["_id"])

    return user


def init_app(app: Flask):
    """ Register any necessary methods with the app """
    app.teardown_appcontext(close_db)
