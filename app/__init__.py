from flask import Flask
from config import Config

from flask_pymongo import PyMongo

app = Flask(__name__)
app.config.from_object(Config)

#Session(app)

mongo = PyMongo(app)

from app import routes
