from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__, instance_relative_config=True)
CORS(app)  

from criptos import routes

app.config.from_object('config')