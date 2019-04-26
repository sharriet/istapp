import os

class Config(object):
    SECRET_KEY = "my super secret key".encode('utf8')
    MONGODB_HOST = os.environ['MONGODB_HOST']
    MONGODB_PORT = 27017

class DevConfig(object):
    SECRET_KEY = "my super secret key".encode('utf8')
    MONGO_URI = "mongodb://localhost:27017/istapp"
    DEBUG = True
