from flask import Flask


def create_app():
    """ create and configure the flask app """
    app = Flask(__name__)

    app.config.from_mapping(
        DB_USER="root",
        DB_PASSWORD="example",
        DB_HOST="mongo",
        DB_PORT=27017,
        SECRET_KEY='dev',
    )

    @app.route("/test")
    def test():
        return "test"

    from .db import init_app
    init_app(app)

    return app
