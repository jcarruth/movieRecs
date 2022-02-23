""" Test behavior of the database module """
from unittest.mock import MagicMock, patch

import mongomock
from movie_recs.db import get_db

from fixtures import AppTestFixture


class DatabaseTest(AppTestFixture):
    """ Test behavior of the database module """

    def test_get_db_instance(self):
        """ get_db should always return the same instance within an app context """
        with self.app.app_context():
            db_first_call = get_db()
            db_second_call = get_db()
            self.assertIs(db_first_call, db_second_call)

    # mongomock.MongoClient.close simply passes.
    # Use a mock to check that it's called
    @patch.object(mongomock.MongoClient, "close", autospec=True)
    def test_leaving_app_context_closes_db(self, mock_close_method: MagicMock):
        """ Any instance of the db connection should be closed when the app context is left """
        with self.app.app_context():
            database = get_db()
            mock_close_method.assert_not_called()

        mock_close_method.assert_called_once_with(database.client)

    @patch("movie_recs.cli.init_db")
    def test_db_initialization(self, mock_init_db):
        """ Ensure that running the init-db command through cli calls init_db method """

        self.app.test_cli_runner().invoke(args=["init-db"])

        mock_init_db.assert_called()
