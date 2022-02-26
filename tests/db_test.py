""" Test behavior of the database module """
from unittest.mock import MagicMock, patch

import mongomock
from movie_recs.db import get_db
from movie_recs.movie_list import top_100_classic_movies
import slugify

from fixtures import AppTestFixture


def get_dummy_movie_data(movie_title):
    """ Return simplified movie data that omdb.get_movie_data would return """
    movie_data = {
        "Title": movie_title,
        "slug": slugify.slugify(movie_title),
        "Synopsis": "Short plot",
        "Plot": "Full plot",
    }

    return movie_data


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

    @patch("movie_recs.cli.get_movie_data", new=get_dummy_movie_data)
    def test_db_initialization(self):
        """ Ensure that running the init-db adds top 100 classic movies to db """

        self.app.test_cli_runner().invoke(args=["init-db"])

        with self.app.app_context():
            database = get_db()
            movies = database.movies
            titles_in_db = [m["Title"] for m in movies.find()]

        titles_in_db.sort()

        self.assertListEqual(titles_in_db, sorted(top_100_classic_movies))
