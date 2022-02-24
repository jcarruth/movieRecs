""" Test behavior of authentication module """

from flask import g, session, url_for
from flask.testing import FlaskClient
from movie_recs.db import get_user_by_username
from typing import Union
from werkzeug.test import TestResponse

from fixtures import AppContextTestFixture


class AuthTest(AppContextTestFixture):
    """ Test behavior of authentication module """

    class InputValidationTestCase:
        """ Helper class bundling register/login inputs and expected message """

        def __init__(self, username: str, password: str, message: str):
            self.data = {
                "username": username,
                "password": password,
            }
            self.message = message

    def setUp(self):
        super().setUp()

        with self.app.test_request_context():
            self.register_url = url_for("auth.register")
            self.login_url = url_for("auth.login")
            self.logout_url = url_for("auth.logout")

    def post(self, url, data, client: Union[FlaskClient, None] = None) -> TestResponse:
        """ Helper function to send a POST """
        if client is None:
            client = self.app.test_client()
        response = client.post(url, data=data)
        return response

    def register_user(self, username="user", password="pass", client: Union[FlaskClient, None] = None) -> TestResponse:
        """ Helper function to easily register a user """

        return self.post(
            self.register_url,
            data={
                "username": username,
                "password": password
            },
            client=client
        )

    def login(self, username="user", password="pass", client: Union[FlaskClient, None] = None) -> TestResponse:
        """ Helper function to easily login """

        return self.post(
            self.login_url,
            data={
                "username": username,
                "password": password
            },
            client=client
        )

    def test_register_is_reachable(self):
        """ Test that the register page can be reached """
        client = self.app.test_client()
        response = client.get(self.register_url)

        self.assertEqual(response.status_code, 200)

    def test_registered_user_added_to_db(self):
        """ Test that a newly registered user can be found in the database """

        username = "user1"
        user_from_db = get_user_by_username(username)
        self.assertIsNone(user_from_db)

        self.register_user(username)

        user_from_db = get_user_by_username(username)
        self.assertIsNotNone(user_from_db)

    def test_successful_registration_redirected_to_login(self):
        """ Test after registering, a user is redirected to the login page """
        response = self.register_user()

        self.assertIn("Location", response.headers)
        redirect_location = response.headers["Location"]

        self.assertIn(self.login_url, redirect_location)

    def test_register_input_validation(self):
        """ Test validation of user input during registration """

        registered_user = "registered"
        self.register_user(registered_user)

        test_cases = [
            self.InputValidationTestCase("", "", b"Username is required"),
            self.InputValidationTestCase("", "a", b"Username is required"),
            self.InputValidationTestCase("a", "", b"Password is required"),
            self.InputValidationTestCase(
                registered_user, "a", b"already registered"),
        ]

        for case in test_cases:
            with self.subTest(case=case):
                response = self.register_user(**case.data)
                redirect_msg = "Implies redirection"
                self.assertNotIn("Location", response.headers, redirect_msg)
                self.assertIn(case.message, response.data)

    def test_login_is_reachable(self):
        """ Test that the register page can be reached """
        client = self.app.test_client()
        response = client.get(self.login_url)

        self.assertEqual(response.status_code, 200)

    def test_logged_in_user_added_to_session(self):
        """ Test that after logging in, the user is available in the session and g """

        username = "user1"
        password = "pass123"
        self.register_user(username, password)

        user_from_db = get_user_by_username(username)

        user_id = str(user_from_db["_id"])

        with self.app.test_client() as client:
            self.login(username, password, client)
            client.get("/")

            self.assertEqual(session["user_id"], user_id)
            self.assertDictEqual(g.user, user_from_db)

    def test_successful_login_redirected_to_root(self):
        """ Test after logging in, the user is redirected to the root page """

        username = "user1"
        password = "pass123"
        self.register_user(username, password)
        response = self.login(username, password)

        self.assertIn("Location", response.headers)
        redirect_location = response.headers["Location"]

        self.assertEqual("http://localhost/", redirect_location)

    def test_login_input_validation(self):
        """ Test validation of user input during login """

        registered_user = "registered"
        registered_password = "registered123"
        self.register_user(registered_user, registered_password)

        test_cases = [
            self.InputValidationTestCase(
                "notRegistered", "a", b"Incorrect username"),
            self.InputValidationTestCase(
                registered_user, "a", b"Incorrect password"),
        ]

        for case in test_cases:
            with self.subTest(case=case):
                response = self.login(**case.data)
                redirect_msg = "Implies redirection"
                self.assertNotIn("Location", response.headers, redirect_msg)
                self.assertIn(case.message, response.data)

    def test_logout_clears_session(self):
        """ Test that logging out clears user out of session and g """

        self.register_user()
        self.login()

        with self.app.test_client() as client:
            client.get(self.logout_url)

            self.assertNotIn("user_id", session)
            self.assertIsNone(g.user)
