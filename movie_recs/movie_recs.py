import random
import requests

from flask import Flask, render_template

app = Flask(__name__)


movies = [
    "It Happened One Night",
    "Citizen Kane",
    "The Wizard of Oz",
    "Modern Times",
    "Casablanca",
    "Sunset Boulevard",
    "All About Eve",
    "The Cabinet of Dr. Caligari",
    "The Philadelphia Story",
    "Rebecca",
    "His Girl Friday",
    "A Night at the Opera",
    "The Third Man",
    "Rear Window",
    "Seven Samurai",
    "La Grande illusion",
    "Singin' in the Rain",
    "All Quiet on the Western Front",
    "Snow White and the Seven Dwarfs",
    "On the Waterfront",
    "An American in Paris",
    "The Best Years of Our Lives",
    "Metropolis",
    "The Kid",
    "Nosferatu",
    "The Adventures of Robin Hood",
    "North by Northwest",
    "Laura",
    "King Kong",
    "Shadow of a Doubt",
    "Psycho",
    "A Hard Day's Night",
    "The Bridge on the River Kwai",
    "Top Hat",
    "The Bride of Frankenstein",
    "12 Angry Men",
    "Marty",
    "The Lady Eve",
    "The Treasure of the Sierra Madre",
    "Lawrence of Arabia",
    "Chinatown",
    "The Lady Vanishes",
    "Dr. Strangelove Or How I Learned to Stop Worrying and Love the Bomb",
    "All the King's Men",
    "The 39 Steps",
    "Frankenstein",
    "The Thin Man",
    "The Gold Rush",
    "Battleship Potemkin",
    "A Streetcar Named Desire",
    "Touch of Evil",
    "Kind Hearts and Coronets",
    "Rashômon",
    "It's a Wonderful Life",
    "Vertigo",
    "The Last Picture Show",
    "The Red Shoes",
    "Scarface",
    "The Grapes of Wrath",
    "The Lost Weekend",
    "The Big Sleep",
    "Goldfinger",
    "Cool Hand Luke",
    "The 400 Blows",
    "Anatomy of a Murder",
    "Stagecoach",
    "Invasion of the Body Snatchers",
    "The Passion of Joan of Arc",
    "Sweet Smell of Success",
    "Paths of Glory",
    "The French Connection",
    "Roman Holiday",
    "Freaks",
    "Bringing Up Baby",
    "2001: A Space Odyssey",
    "In the Heat of the Night",
    "In a Lonely Place",
    "Night of the Living Dead",
    "Gentlemen Prefer Blondes",
    "Rosemary's Baby",
    "Sunrise",
    "The Day the Earth Stood Still",
    "Detour",
    "Mrs. Miniver",
    "City Lights",
    "Miracle on 34th Street",
    "Home of the Brave",
    "Gone With the Wind",
    "Badlands",
    "Repulsion",
    "The Leopard",
    "101 Dalmatians",
    "The Manchurian Candidate",
    "The Blue Angel",
    "Children of Paradise",
    "Kiss Me Deadly",
    "Stormy Weather",
    "One Flew Over the Cuckoo's Nest",
    "The Invisible Man",
    "The African Queen",
]


@app.route("/random")
def random_movie():
    """Recommends a random movie

    Returns:
        [type]: [description]
    """
    movie = random.choice(movies)

    params = {
        "apikey": "d1e1fd79",
        "t": movie,
        "plot": "short"
    }

    response = requests.get("http://www.omdbapi.com/", params=params)

    synopsis = response.json()["Plot"]

    params["plot"] = "full"
    response = requests.get("http://www.omdbapi.com/", params=params)
    data = response.json()
    data["Synopsis"] = synopsis

    return render_template("movie.html", **data)
