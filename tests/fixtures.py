""" Test fixtures to provide easier setup and tear down of application """

import contextlib
import unittest
from typing import Optional

import mongomock
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
            self.addCleanup(stack.pop_all().close)

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
