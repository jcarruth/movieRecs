from flask import Flask


def create_app():
    """ create and configure the flask app """
    app = Flask(__name__)

    @app.route("/test")
    def test():
        return "test"

    return app
