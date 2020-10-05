
from flask import Flask, jsonify
from config import config
from pymongo import MongoClient
from project import routes, models

import json

app = Flask(__name__)
client = MongoClient(config['MONGODB_SETTINGS']['host'], config['MONGODB_SETTINGS']['port'])
db = client[config['MONGODB_SETTINGS']['db']]

if __name__ == "__main__":
    routes.init_app(app)
    app.run(debug=True)