""" Test the interface to the Open Movie Database """

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

        short_params = {
            "apikey": TEST_OMDB_API_KEY,
            "t": self.test_movie_title,
            "plot": "short"
        }

        full_params = short_params.copy()
        full_params["plot"] = "full"

        self.short_response = {
            "Response": True,
            "Title": self.test_movie_title,
            "Plot": self.short_plot,
        }
        self.full_response = self.short_response.copy()
        self.full_response["Plot"] = self.full_plot

        responses.add(
            responses.GET,
            "http://www.omdbapi.com",
            json=self.short_response,
            match=[responses.matchers.query_param_matcher(short_params)],
        )

        responses.add(
            responses.GET,
            "http://www.omdbapi.com",
            json=self.full_response,
            match=[responses.matchers.query_param_matcher(full_params)],
        )

        responses.add(
            responses.GET,
            "http://www.omdbapi.com",
            json={"Response": False},
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
