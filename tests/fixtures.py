""" Test fixtures to provide easier setup and tear down of application """

import unittest
import contextlib

import mongomock
from movie_recs import create_app
from movie_recs.db import init_collections

TEST_MONGO_HOST = "localhost"


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
