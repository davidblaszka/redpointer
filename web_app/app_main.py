from flask import Flask, url_for, request, render_template, Markup,redirect
from pymongo import MongoClient
import pandas as pd
from datetime import date
import time
import atexit
import numpy as np
from find_recommendations import (recommender, item_by_item_matrix)


app = Flask(__name__)
PORT = 8080

@app.route('/')
def root():
	# find top routes in washington
	df = pd.DataFrame(list(routes.find()))
	df_sorted= df.sort_values('page_views', ascending=False).head(20)
	recs = df_sorted.sort_values('average_rating', ascending=False).head(6)
	return render_template('index.html', routes=recs)


@app.route('/returning-user', methods=['GET', 'POST'])
def getReturnRatings():
	routes = db.routes.find({})
	return render_template('recommender.html', routes=routes)


@app.route('/new-user', methods=['GET', 'POST'])
def getNewRatings():
	routes = db.routes.find({})
	return render_template('recommender.html', routes=routes)


@app.route('/my-recommendations', methods=['POST', 'GET'])
def getRecs():
	route_name = request.args.get('route-name')
	route_type = request.args.get('route-type')
	route_grade_gr = request.args.get('route-grade_gr')
	route_grade_ls = request.args.get('route-grade_ls')
	username = request.args.get('username')
	recs = recommender(username, route_name, route_grade_gr, 
								route_grade_ls, route_type)
	return render_template('my-recommendations.html', recs=recs)
# Shut down the scheduler when exiting the app
#atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
	# Register for pinging service

	# Connect to the database
	client = MongoClient()
	db = client.routes_updated
	routes = db.routes

	# Start Flask app
	app.run(host='0.0.0.0', port=PORT, threaded=True, debug=True)
