import os

class Config(object):
    SECRET_KEY = "my super secret key".encode('utf8')
    MONGO_URI = "mongodb://localhost:27017/istapp"
