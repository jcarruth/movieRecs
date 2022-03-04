""" Provides access to the Open Movie Database """
import requests
from flask import current_app
from slugify import slugify


def get_movie_data(movie_title: str) -> dict:
    """ Get data for a movie title """

    params = {
        "apikey": current_app.config["OMDB_API_KEY"],
        "t": movie_title,
        "plot": "short"
    }

    response = requests.get("http://www.omdbapi.com/", params=params)

    content_type = response.headers.get("Content-Type", "plain/text")
    response_contains_json = content_type == "application/json"

    response_json = response.json() if response_contains_json else {}

    if response.status_code >= 400 or response_json.get("Response", "False") == "False":
        if "Error" in response_json:
            if response_json["Error"] == "Movie not found!":
                raise LookupError(
                    f"Movie \"{movie_title}\" not found in OMDB.")
            raise Exception(response_json["Error"])
        raise Exception("An unknown error occurred")

    synopsis = response_json["Plot"]

    params["plot"] = "full"
    response = requests.get("http://www.omdbapi.com/", params=params)
    movie_data = response.json()
    movie_data["Synopsis"] = synopsis
    movie_data["slug"] = slugify(movie_data["Title"])

    return movie_data
