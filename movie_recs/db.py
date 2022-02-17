from pymongo import MongoClient

from flask import Flask, current_app, g


def get_db() -> MongoClient:
    """Provides access to the database"""

    if "db" not in g:
        username = current_app.config["DB_USER"]
        password = current_app.config["DB_PASSWORD"]
        host = current_app.config["DB_HOST"]
        port = current_app.config["DB_PORT"]
        uri = f"mongodb://{username}:{password}@{host}:{port}"
        g["db"] = MongoClient(uri)

    return g.db


def close_db():
    """ Closes the database connection """
    db: MongoClient = g.pop("db", None)

    if db is not None:
        db.close()


def init_app(app: Flask):
    """ Register any necessary methods with the app """
    app.teardown_appcontext(close_db)
