""" Test the interface to the Open Movie Database """
import json
from typing import NamedTuple, Optional

import responses
from movie_recs import omdb

from fixtures import TEST_OMDB_API_KEY, AppContextTestFixture


class TestOmdbInterface(AppContextTestFixture):
    """ Test the interface to the Open Movie Database """

    def setUp(self):
        super().setUp()

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

    def assert_dict_contains_dict(self, test_dict: dict, sub_dict: dict):
        """ Replacement for unittest.assertDictContainsSubset """
        test_sub_dict = {k: test_dict.get(k, None) for k in sub_dict.keys()}
        self.assertEqual(test_sub_dict, sub_dict)

    @responses.activate
    def test_get_movie_data_contains_title(self):
        """ Test that the returned movie data includes the title """
        movie_data = omdb.get_movie_data(self.test_movie_title)

        title_data = {"Title": self.test_movie_title}
        self.assert_dict_contains_dict(movie_data, title_data)

    @responses.activate
    def test_get_movie_data_contains_synopsis(self):
        """ Test that the returned movie data includes the synopsis """
        movie_data = omdb.get_movie_data(self.test_movie_title)

        synopsis_data = {"Synopsis": self.short_plot}
        self.assert_dict_contains_dict(movie_data, synopsis_data)

    @responses.activate
    def test_get_movie_data_contains_plot(self):
        """ Test that the returned movie data includes the plot """
        movie_data = omdb.get_movie_data(self.test_movie_title)

        plot_data = {"Synopsis": self.short_plot}
        self.assert_dict_contains_dict(movie_data, plot_data)

    @responses.activate
    def test_get_movie_data_contains_slug(self):
        """ Test that the returned movie data includes the expected slug """
        movie_data = omdb.get_movie_data(self.test_movie_title)

        slug_data = {"slug": self.expected_slug}
        self.assert_dict_contains_dict(movie_data, slug_data)

    @responses.activate
    def test_get_movie_data_missing_movie(self):
        """ Test that a relevant exception is thrown when a movie is not found """
        with self.assertRaises(LookupError):
            omdb.get_movie_data("My Home Movie 1998")

    @responses.activate
    def test_invalid_api_key_handled(self):
        """ Test that a relevant exception is thrown when a movie is not found """
        self.app.config.from_mapping(OMDB_API_KEY="not a real key")

        with self.assertRaises(Exception) as e:
            omdb.get_movie_data(self.test_movie_title)

        self.assertIn("Invalid OMDB api key!", str(e.exception))

    @responses.activate
    def test_general_errors_handled(self):
        """ Test that a relevant exception is thrown when a movie is not found """

        class GeneralErrorTestCase(NamedTuple):
            """ Helper class bundling general errors responses from OMDB """
            status: int
            response_data: Optional[dict]

        test_cases = [
            GeneralErrorTestCase(403, None),
            GeneralErrorTestCase(404, None),
            GeneralErrorTestCase(200, {}),
            GeneralErrorTestCase(200, {"Response": "False"}),
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):

                responses.replace(
                    responses.GET,
                    "http://www.omdbapi.com",
                    status=test_case.status,
                    json=test_case.response_data
                )

                with self.assertRaises(Exception) as e:
                    omdb.get_movie_data(self.test_movie_title)

                self.assertIn("An unknown error occurred", str(e.exception))
