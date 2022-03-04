""" Test fixtures to provide easier setup and tear down of application """

import contextlib
import json
import unittest
from typing import Optional

import mongomock
import responses
from flask import url_for
from flask.testing import FlaskClient
from movie_recs import create_app
from movie_recs.db import init_collections
from werkzeug.test import TestResponse

TEST_MONGO_HOST = "localhost"
TEST_OMDB_API_KEY = "TEST_OMDB_API_KEY"


class AppTestFixture(unittest.TestCase):
    """ Fixture to provide an app instance in testing mode with a mocked database """

    def setUp(self):
        with contextlib.ExitStack() as stack:
            stack.enter_context(mongomock.patch(servers=TEST_MONGO_HOST))
            stack.enter_context(responses.mock)
            self.addCleanup(stack.pop_all().close)

        self.test_movie_title = "The Imitation Game"
        self.expected_slug = "the-imitation-game"
        self.short_plot = "Short plot"
        self.full_plot = "Full plot"

        def request_callback(request):
            """ Generate an appropriate response for the request params """

            params: dict = request.params
            response_body = {}

            if "apikey" not in params or params["apikey"] != TEST_OMDB_API_KEY:
                response_body["Response"] = "False"
                response_body["Error"] = "Invalid OMDB api key!"

            elif params["t"] != self.test_movie_title:
                response_body["Response"] = "False"
                response_body["Error"] = "Movie not found!"
            else:
                response_body["Response"] = "True"
                response_body["Title"] = self.test_movie_title

                if params.get("plot", "short") == "short":
                    response_body["Plot"] = self.short_plot
                else:
                    response_body["Plot"] = self.full_plot

            headers = {'request-id': '728d329e-0e86-11e4-a748-0c84dc037c13'}
            return (200, headers, json.dumps(response_body))

        responses.add_callback(
            responses.GET,
            "http://www.omdbapi.com",
            callback=request_callback,
            content_type='application/json',
        )

        self.app = create_app(
            {
                "TESTING": True,
                "DB_HOST": TEST_MONGO_HOST,
                "OMDB_API_KEY": TEST_OMDB_API_KEY,
            }
        )

        with self.app.app_context():
            init_collections()


class AppContextTestFixture(AppTestFixture):
    """ Fixture for running tests within the app context """

    def setUp(self):
        super().setUp()

        with contextlib.ExitStack() as stack:
            stack.enter_context(self.app.app_context())
            self.addCleanup(stack.pop_all().close)


class AuthenticationTestFixture(AppContextTestFixture):
    """ Fixture for running tests that requiring logging in """

    default_username = "default_username"
    default_password = "default_password"

    def setUp(self):
        super().setUp()

        self.register_user()

    def post(self, url, data, client: Optional[FlaskClient] = None) -> TestResponse:
        """ Helper function to send a POST """
        if client is None:
            client = self.app.test_client()
        response = client.post(url, data=data)
        return response

    def register_user(
        self,
        username=default_username,
        password=default_password,
        client: Optional[FlaskClient] = None
    ) -> TestResponse:
        """ Helper function to easily register a user """

        with self.app.test_request_context():
            register_url = url_for("auth.register")

        return self.post(
            register_url,
            data={
                "username": username,
                "password": password
            },
            client=client
        )

    def login(
        self,
        username=default_username,
        password=default_password,
        client: Optional[FlaskClient] = None
    ) -> TestResponse:
        """ Helper function to easily login """

        with self.app.test_request_context():
            login_url = url_for("auth.login")

        return self.post(
            login_url,
            data={
                "username": username,
                "password": password
            },
            client=client
        )

    def logout(self, client: Optional[FlaskClient] = None):
        """ Helper function to easily logout """

        with self.app.test_request_context():
            logout_url = url_for("auth.logout")

        client.get(logout_url)
