""" Test behavior of movies module """

import html

import responses
from flask import url_for

from fixtures import TEST_OMDB_API_KEY, AuthenticationTestFixture


class MoviesTest(AuthenticationTestFixture):
    """ Test behavior of movies module """

    def setUp(self):
        super().setUp()

        with self.app.test_request_context():
            self.add_url = url_for("movies.add")

        self.test_movie_title = "The Imitation Game"
        self.expected_slug = "the-imitation-game"
        self.short_plot = "Short plot"
        self.full_plot = "Full plot"
        self.nonexistent_movie_title = "Some Nonexistent Title"

        short_params = {
            "apikey": TEST_OMDB_API_KEY,
            "t": self.test_movie_title,
            "plot": "short"
        }

        full_params = short_params.copy()
        full_params["plot"] = "full"

        short_response = {
            "Response": "True",
            "Title": self.test_movie_title,
            "Plot": self.short_plot,
        }
        full_response = short_response.copy()
        full_response["Plot"] = self.full_plot

        responses.add(
            responses.GET,
            "http://www.omdbapi.com",
            json=short_response,
            match=[responses.matchers.query_param_matcher(short_params)],
        )

        responses.add(
            responses.GET,
            "http://www.omdbapi.com",
            json=full_response,
            match=[responses.matchers.query_param_matcher(full_params)],
        )

        # TODO: once there's a new version of responses, make param match non-strict
        short_params = {
            "apikey": TEST_OMDB_API_KEY,
            "t": self.nonexistent_movie_title,
            "plot": "short"
        }

        full_params = short_params.copy()
        full_params["plot"] = "full"
        responses.add(
            responses.GET,
            "http://www.omdbapi.com",
            json={"Response": "False", "Error": "Movie not found!"},
            match=[responses.matchers.query_param_matcher(short_params)],
        )
        responses.add(
            responses.GET,
            "http://www.omdbapi.com",
            json={"Response": "False", "Error": "Movie not found!"},
            match=[responses.matchers.query_param_matcher(full_params)],
        )

    def test_add_movie_is_reachable(self):
        """ Test that the add movie page can be reached """

        client = self.app.test_client()
        self.login(client=client)

        response = client.get(self.add_url)

        self.assertEqual(response.status_code, 200)

    def test_add_movie_requires_title(self):
        """ Test that adding a movie requires an movie title in the input"""

        client = self.app.test_client()
        self.login(client=client)

        response = client.post(self.add_url, data={"movie_title": ""})
        redirect_msg = "Implies redirection"

        self.assertNotIn("Location", response.headers, redirect_msg)
        self.assertIn(b"A movie title is required", response.data)

    @responses.activate
    def test_add_movie_not_found_in_omdb(self):
        """ Test that trying to add a movie that's not in OMDB gives a message """

        client = self.app.test_client()
        self.login(client=client)

        response = client.post(self.add_url, data={
                               "movie_title": self.nonexistent_movie_title})

        self.assertNotIn("Location", response.headers, "Implies redirection")

        expected_message = f"The movie \"{self.nonexistent_movie_title}\" was not found in the OMDB"
        response_data = html.unescape(response.get_data(as_text=True))
        self.assertIn(expected_message, response_data)

    @responses.activate
    def test_add_movie_already_added(self):
        """ Test that adding a movie that's already added gives a message """

        client = self.app.test_client()
        self.login(client=client)

        data = {"movie_title": self.test_movie_title}
        client.post(self.add_url, data=data)
        response = client.post(self.add_url, data=data)

        self.assertNotIn("Location", response.headers, "Implies redirection")

        expected_message = f"The movie \"{self.test_movie_title}\" has already been added"
        response_data = html.unescape(response.get_data(as_text=True))
        self.assertIn(expected_message, response_data)

    @responses.activate
    def test_add_movie_redirect_on_add(self):
        """ Test that successfully adding a movie redirects to movie details """

        client = self.app.test_client()
        self.login(client=client)

        data = {"movie_title": self.test_movie_title}
        response = client.post(self.add_url, data=data)

        self.assertIn("Location", response.headers, "Implies redirection")

        with self.app.test_request_context():
            detail_url = url_for("movies.movie_details",
                                 slug=self.expected_slug)

        expected_redirect = "http://localhost" + detail_url

        self.assertEqual(response.location, expected_redirect)
