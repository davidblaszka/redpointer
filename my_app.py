from flask import Flask, request, render_template
import json
import requests
import socket
import time
from datetime import datetime
from pymongo import MongoClient
import pandas as pd


app = Flask(__name__)
PORT = 5353

@app.route('/', methods=['GET'])
def index():
    return render_template('home.html')


if __name__ == '__main__':

    # Start Flask app
    app.run(host='0.0.0.0', port=PORT, debug=True)
