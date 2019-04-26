from flask import Flask
from config import Config

#from flask_pymongo import PyMongo # local deploy
from pymongo import MongoClient

app = Flask(__name__)
app.config.from_object(Config)

#mongo = PyMongo(app) # local deploy

client = MongoClient(app.config['MONGODB_HOST'])
mongo = client.istapp

from app import routes
