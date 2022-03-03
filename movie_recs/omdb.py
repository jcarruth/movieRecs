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

    response_json = response.json()

    if "Response" not in response_json or response_json["Response"] == "False":
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
