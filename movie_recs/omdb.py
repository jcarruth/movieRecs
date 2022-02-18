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

    if "Response" not in response.json() or not response.json()["Response"]:
        raise Exception("")

    synopsis = response.json()["Plot"]

    params["plot"] = "full"
    response = requests.get("http://www.omdbapi.com/", params=params)
    movie_data = response.json()
    movie_data["Synopsis"] = synopsis
    movie_data["slug"] = slugify(movie_data["Title"])

    return movie_data
