from flask import render_template, request, redirect, url_for, session, flash
from app import app, mongo
from random import randint
from string import ascii_letters
import string

=======
import speech_to_text as stt
>>>>>>> dd99535f88ea78c5a560e330571994d57c3cf258

# ----------------------
# GAME FRAMEWORK ROUTES
# ----------------------

@app.route('/')
def index():
    """ landing page. user can generate a game pin
        or join game with existing pin. if game pin
        in URL it will go straight to map.
    """
    pin = request.args.get('pin')
    if pin is not None and pin_exists(pin):
        return redirect( url_for('phys-index') )
    else:
        return render_template('home.html', page="Home")

@app.route('/join')
def join():
    """ user joins game automatically if pin in query
        string else prompted to enter their game pin
    """
    pin = request.args.get('pin')
    if pin is not None and pin_exists(pin):
        if request.args.get('resume') is not None:
            update_strength(pin, "persistent")
        else:
            update_strength(pin, "explorative")
        return render_template('phys-index.html')
    else:
        return render_template('join.html', page="Resume game")

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
        return render_template('pingen.html', pin=pin, success=True, page="Generate game pin")
    else:
        return render_template('pingen.html', success=False, page="Oops!")

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
        return render_template('pingen.html', success=False, page="Oops!")

@app.route('/end')
def end():
    """ option to exit game
    """
    pin = request.args.get('pin')
    if pin is not None and pin_exists(pin):
        return render_template("end.html", pin=pin, page="exit game")
    else:
        return redirect( url_for('index') )

@app.route('/score')
def score():
    pin = request.args.get('pin')
    if pin is not None:
        cur = mongo.db.profiles.find({"game_pin": pin}).limit(1)
        if cur.count() > 0:
            print(cur)
            docs = [doc for doc in cur]
            best_role = get_best_role(docs[0])
            cur = mongo.db.roles.find({"title": best_role}).limit(1)
            docs = [doc for doc in cur] 
            return render_template('score.html', page='scoreboard', role=docs[0])
        else:
            return render_template('score.html', page='scoreboard')
    else:
        return redirect( url_for('index') )

@app.route('/task')
def task():
    """ route for performing tasks """
    task_name = request.args.get('task')
    pin = request.args.get('pin')
    if task_name is not None and task_exists(task_name) \
            and pin is not None and pin_exists(pin):
        cur = mongo.db.tasks.find({"task_name":task_name}).limit(1)
        docs = [doc for doc in cur] 
        return render_template('task.html', pin=pin, task=docs[0], page='Take task')
    else:
        return redirect( url_for('index', pin=pin) )

@app.route('/task-submit', methods=["GET", "POST"])
def task_submit():
    """ handles a user response to a task """
    if request.method == "POST":
        strength = request.form["strength"]
        pin = request.form["pin"]
        if len(strength) > 0:
            strengths = strength.split(",")
            for s in strengths:
                update_strength(pin, s)
        return render_template( 'task-response.html', pin=pin, page="Task response" )
    else:
        pin = request.args.get('pin')
        return redirect( url_for('index', pin=pin) )

# ------------------------------------------
# ROUTES ASSOCIATED WITH SPECIFIC SCENARIOS
# ------------------------------------------
# SCENARIOS 1
@app.route('/phys-index')
def phys_index():
    """ the fake Genome Tech home view """
    if session.get('encrypted'):
        # will show raw data sample with encryption
        return render_template('phys-encrypt-index.html', ciphertext_list = session['ciphertext_list'], page='Genome Tech DB: Home')
    else:
        # will show same raw data sample without encryption
        return redirect(url_for('phys-index.html'))

# this is the encryption method
@app.route('/phys-encrypt', methods=["GET", "POST"])
def phys_encrypt_index():
    """ the fake Genome Tech encryption view """
    if request.method == "POST":
        #en_method = request.form["encrypt_method"]
        en_key = int(request.form["encrypt_key"])
        if en_key != None and en_key >= 1 and en_key <= 25:
            ciphertext_list = []
            plaintext_list = ["sample", "hg00512", "hg00701", "na18525", "na90918", "sex", "male", "female", "male", "female", "chromosome", "1", "1", "1", "1", "age", "32", "51", "44", "26", "allele 1", 
"a", "a", "g", "g", "allele 2", "a", "a", "g", "g"]
            for plaintext in plaintext_list:
                ciphertext_list.append(caesar(plaintext, en_key))
            
            session['encrypted'] = True
            session['key'] = en_key
            session['ciphertext_list'] = ciphertext_list
            return render_template('phys-encrypt-index.html', ciphertext_list = ciphertext_list)
        else:
            # should be with error
            flash ("please insert a valid key")
            return render_template('phys-index.html',  page='Genome Tech DB: Home')
    else:
        #without error
        return render_template('phys-index.html',  page='Genome Tech DB: Home')

# this is the decryption method
@app.route('/phys-decrypt', methods=["GET", "POST"])
def phys_decrypt_index():
    """ the fake Genome Tech decryption view """
    if request.method == "POST":
        en_key = int(request.form["decrypt_key"])
        if en_key != None and en_key >= 1 and en_key <= 25:
            if en_key == session['key']:
                session['decrypted'] = True
                return render_template('phys-index.html')
            else:
                flash('key is not correct')
                return render_template('phys-encrypt-index.html', ciphertext_list = session['ciphertext_list'])
        else:
            flash('inser a valid key')
            return render_template('phys-index', page="Genome Tech DB: Login")


# SCENARIOS 2
@app.route('/desktop-hackers-index')
def desktop_hackers_index():
    """ the fake Genome Tech home view """
    if session.get('logged_in'):
        return render_template('gt-index.html', page='Genome Tech DB: Home')
    else:
        return redirect(url_for('desktop_hackers_login'))

@app.route('/desktop-hackers-login', methods=["GET", "POST"])
def desktop_hackers_login():
    """ the fake Genome Tech login view """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "b.jameson" and password == "alice2009":
            session['logged_in'] = True
            return redirect(url_for('desktop_hackers_index'))
        else:
            errs = []
            if username != "b.jameson":
                errs.append("username")
            if password != "alice2009":
                errs.append("password")
            return render_template('gt-login.html', page="Genome Tech DB: Login", errs=errs)
    else:
        return render_template('gt-login.html', page="Genome Tech DB: Login")

@app.route('/desktop-hackers-submit', methods=["GET", "POST"])
def desktop_hackers_submit():
    """ what gets shown after action performed
        in fake Genome Teck app
    """
    if session.get('logged_in'):
        response_text = ""
        if request.method == "POST":
            cur = mongo.db.tasks.find({"task_name": "desktop-hackers"}).limit(1)
            docs = [doc for doc in cur]
            for outcome in docs[0]["outcomes"]:
                if outcome["action"] == request.form["action"]:
                    response = "Success"
                    response_text = outcome["system_response"]
        if len(response_text) == 0:
            response = "Fail"
            response_text = "Oops! Something went wrong. Please go back and try again."
        session['logged_in'] = False # log them out automatically
        return render_template('gt-response.html', page='Genome Tech DB: Confirm action', response=response, response_text=response_text)
    else:
        return redirect(url_for('desktop_hackers_login'))

@app.route('/sorting-sorters')
def sorting_sorters():
    """ response to user input view for sorting sorters scenario
    """
    resp = stt.listen_for_speech(trigwords=["bubble", "merge"])
    if resp == "bubble":
        return render_template("sorters.html", page="Webchat", alg="bubble")
    elif resp == "merge":
        return render_template("sorters.html", page="Webchat", alg="merge")
    else:
        return render_template("sorters.html", page="Webchat", alg="unsure")

@app.route('/sorting-sorters-intro')
def sorting_sorters_intro():
    """ intro view for sorting sorters task
    """
    return render_template("sorting-sorters-intro.html")

@app.route('/sorting-sorters-end')
def sorting_sorters_end():
    """ view when call is ended in sorting sorters task
    """
    return render_template("sorting-sorters-end.html")

# --------------------
# GAMEPLAY FUNCTIONS
# --------------------

def encrypt_data(en_method, en_key):
    """ encrypt the fake raw data sample in the genome tech db
    """
    return data

def caesar(plaintext, shift):
 #   alphabet = string.ascii_lowercase
  #  shifted_alphabet = alphabet[shift:] + alphabet[:shift]
   # table = str.maketrans(alphabet, shifted_alphabet)
    #return plaintext.translate(table)
	
	#shift %= 26 # Values greater than 26 will wrap around

	alphabet_lower = string.ascii_lowercase
	alphabet_upper = string.ascii_uppercase

	shifted_alphabet_lower = alphabet_lower[shift:] + alphabet_lower[:shift]
	shifted_alphabet_upper = alphabet_upper[shift:] + alphabet_upper[:shift]

	alphabet = alphabet_lower + alphabet_upper 
	shifted_alphabet = shifted_alphabet_lower + shifted_alphabet_upper

	table = str.maketrans(alphabet, shifted_alphabet) 

	return plaintext.translate(table)
	
def update_strength(pin, strength):
    """ increment a strength in a specified profile
    """
    result = mongo.db.profiles.update(
            { "$or" : [
                {"game_pin" : pin, "strengths."+strength: {"$exists": False}},
                {"game_pin": pin, "strengths."+strength: { "$lt": 5, "$gte": 0 }}]},
            {"$inc": {"strengths."+strength: 1} } )
    return result

def pin_exists(pin):
    """ check if pin exists """
    cur = mongo.db.profiles.find({"game_pin": pin}).limit(1)
    if cur.count() > 0:
        return True
    else:
        return False

def task_exists(task_name):
    """ check if specified task exists """
    cur = mongo.db.tasks.find({"task_name": task_name}).limit(1)
    if cur.count() > 0:
        return True
    else:
        return False

def get_best_role(doc):
    """ calcs best fitting cs role for a profile document """
    roles = mongo.db.roles.find()
    best_score = 20
    for role in roles:
        score = 0
        for key, value in role["strengths"].items():
            if key in doc["strengths"]:
                diff = abs(value - doc["strengths"][key])
            else:
                diff = 5
            score += diff
        if score < best_score:
            best_score = score
            result = role["title"]
    if result:
        return result
    else:
        return False
