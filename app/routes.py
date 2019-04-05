from flask import render_template, request, redirect, url_for
from app import app, mongo
from random import randint
from string import ascii_letters

@app.route('/')
def index():
    """ landing page. user can generate a game pin
        or join game with existing pin. if game pin
        in URL it will go straight to map.
    """
    try:
        game_pin = request.args.get('game_pin')
        profile = mongo.db.profiles.find_one({"game_pin": game_pin})
        game_pin = profile['game_pin']
    except KeyError:
        return render_template('home.html')
    else:
        return redirect(url_for('map', game_pin=profile['game_pin']))

@app.route('/join')
def join():
    """ user can join game by entering their game pin
    """
    return "Join game. #todo"

@app.route('/pingen')
def pingen():
    """ user can generate a unique game pin
    """
    pin = ""
    for i in range(0,5):
        pin += ascii_letters[randint(0,len(ascii_letters))]
    _id = mongo.db.profiles.insert_one({"game_pin": pin})
    if _id.inserted_id:
        return "Success. Pin is {}. #todo now join game!".format(pin)
    else:
        return "Failed to make pin. #todo go try again!"

@app.route('/map')
def map():
    """ a map of locations and clues for each location
    """
    return "Look at the map. #todo"
