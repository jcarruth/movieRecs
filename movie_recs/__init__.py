import os

from flask import Flask


def create_app(test_config=None):
    """ create and configure the flask app """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        DB_USER="root",
        DB_PASSWORD="example",
        DB_HOST="mongo",
        DB_PORT=27017,
        DB_NAME="movie_recs",
        SECRET_KEY='dev',
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/test")
    def test():
        return "test"

    from .db import init_app
    init_app(app)

    from .cli import add_cli_commands
    add_cli_commands(app)

    return app
