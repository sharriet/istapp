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
    pin = request.args.get('pin')
    if pin is not None:
        if pin_exists(pin):
            redirect(url_for('map', pin=pin))
        else:
            return render_template('home.html', page="home")
    else:
        return render_template('home.html', page="home")

@app.route('/join')
def join():
    """ user joins game automatically if pin in query
        string else prompted to enter their game pin
    """
    pin = request.args.get('pin')
    if pin is not None and pin_exists(pin):
        result = update_strength(pin, "curiosity", 1)
        if result["nModified"] > 0:
            return redirect(url_for('map', pin=pin))
        else:
            return render_template('pingen.html', success=False)
    else:
        return render_template('join.html', page="resume game")

@app.route('/pingen')
def pingen():
    """ user can generate a unique game pin
    """
    pin = ""
    for i in range(0,5):
        pin += ascii_letters[randint(0,len(ascii_letters)-1)]
    if not pin_exists(pin):
        _id = mongo.db.profiles.insert_one({"game_pin": pin})
    if _id.inserted_id:
        return render_template('pingen.html', pin=pin, success=True)
    else:
        return render_template('pingen.html', success=False)

@app.route('/map')
def map():
    """ a map of locations and clues for each location
    """
    pin = request.args.get('pin')
    if pin is not None and pin_exists(pin):
        gf_rooms = mongo.db.rooms.find({"floor": 0})
        ff_rooms = mongo.db.rooms.find({"floor": 1})
        return render_template('map.html', gf_rooms=gf_rooms,
                ff_rooms=ff_rooms, pin=pin, page="map")
    else:
        return render_template('pingen.html', success=False)

# --------------------
# GAMEPLAY FUNCTIONS
# --------------------

def update_strength(pin, strength, amount):
    """ increase/decrease a strength in a specified
        profile
    """
    result = mongo.db.profiles.update(
            {"game_pin" : pin},
            {"$inc": {"strengths."+strength: amount} } )
    return result

def pin_exists(pin):
    """ check if pin exists """
    cur = mongo.db.profiles.find({"game_pin": pin}).limit(1)
    if cur.count() > 0:
        return True
    else:
        return False

