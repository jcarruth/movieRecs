""" Manages connection to a mongoDb database """

from bson.objectid import ObjectId
from flask import Flask, current_app, g
import pymongo


def get_db() -> pymongo.database.Database:
    """Provides access to the database"""

    if "database" not in g:
        username = current_app.config["DB_USER"]
        password = current_app.config["DB_PASSWORD"]
        host = current_app.config["DB_HOST"]
        port = current_app.config["DB_PORT"]
        uri = f"mongodb://{username}:{password}@{host}:{port}"
        client = pymongo.MongoClient(uri)
        g.database = client[current_app.config["DB_NAME"]]

    return g.database


def close_db(_=None):
    """ Closes the database connection """
    database: pymongo.database.Database = g.pop("database", None)

    if database is not None:
        database.client.close()


def clear_db():
    """ Clear all collections from database """
    database = get_db()

    for collection in database.list_collection_names():
        database.drop_collection(collection)


def init_collections():
    """ Set up collections in database with indices """
    database = get_db()

    database.movies.create_index("slug", unique=True)
    database.users.create_index("username", unique=True)


def add_movie(movie_data: dict):
    """ Adds a single movie to the database """
    database = get_db()
    movie_collection = database.movies
    movie_collection.insert_one(movie_data)


def get_movies():
    """ Returns a list of movies"""

    database = get_db()
    movie_collection = database.movies

    return list(movie_collection.find())


def get_movie_by_slug(slug: str):
    """ Returns a list of movies"""

    database = get_db()
    movie_collection = database.movies

    return movie_collection.find_one({"slug": slug})


def add_user(username: str, password_hash: str):
    """ Add a user to the database """

    user_data = {
        "username": username,
        "password_hash": password_hash,
    }

    database = get_db()
    database.users.insert_one(user_data)


def get_user_by_username(username: str):
    """ Look up a user using their username """
    database = get_db()

    user = database.users.find_one({"username": username})

    if user is not None:
        user["_id"] = str(user["_id"])

    return user


def get_user_by_id(user_id: str):
    """ Look up a user using their id """
    database = get_db()

    user = database.users.find_one({"_id": ObjectId(user_id)})

    if user is not None:
        user["_id"] = str(user["_id"])

    return user


def init_app(app: Flask):
    """ Register any necessary methods with the app """
    app.teardown_appcontext(close_db)
