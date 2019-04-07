# 4000 Immersive Game: 'ISTApp'

**Under development!**

A simple interactive storytelling app.

This application provides the basic framework for any number of interactive storytelling games.

Fork and edit for your own scenario!

## Prerequisites

To run this version of the app locally you need to have Python 3 and venv installed on your machine.

For help using Python virtual environments, please refer to the [venv documentation](https://docs.python.org/3/library/venv.html).

You also need MongoDB version 3.6.9. The app will most likely work with versions of MongoDB >=3.2 but it has not been tested.

## Installation

To prepare the dev environment on your machine,

+ Clone the repo inside a Python 3 virtual environment (venv)
+ Use pip to install packages listed in requirements.txt:

		pip install -r requirements.txt
+ Rename `config.py.example` as `config.py`
+ Edit the mongo URI if neccessary

## Running the app

+ First initialise the database:
		
		mongoimport --db istapp --collection rooms --type json --file rooms.json --jsonArray
		mongoimport --db istapp --collection roles --type json --file roles.json --jsonArray

+ Now you can run it:

		python run.py
+ App should be available at [0.0.0.0:5000](http://0.0.0.0:5000)
