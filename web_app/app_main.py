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
	df = pd.DataFrame(list(routes.find())).sort_values('page_views', ascending=False).head(20)
	recs = df.sort_values('average_rating', ascending=False).head(6)
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
	route_name =  request.args.get('route-name')
	route_id = list(routes.find({'name': route_name}))[0]['id']
	if request.args.get('username') == '':
		# load routes_Df
		routes_df = pd.read_csv("../data/routes_df.csv", sep='\t').drop('Unnamed: 0', axis=1)
		# compute item-by-item similarity
		cos_sim, route_id_list = item_by_item_matrix(routes_df)
		n = 5
		arr = cos_sim[route_id]
		similar_routes = np.asarray(route_id_list)[arr.argsort()[-(n+1):][::-1][1:]].tolist()
		recs = list(routes.find({"id": {"$in": similar_routes}}))
	elif db.users.find({'name': request.args.get('username')}).count()==0:
		# if username not found
		# load routes_Df
		routes_df = pd.read_csv("../data/routes_df.csv", sep='\t').drop('Unnamed: 0', axis=1)
		# compute item-by-item similarity
		cos_sim, route_id_list = item_by_item_matrix(routes_df)
		n = 5
		arr = cos_sim[route_id]
		similar_routes = np.asarray(route_id_list)[arr.argsort()[-(n+1):][::-1][1:]].tolist()
		recs = list(routes.find({"id": {"$in": similar_routes}}))
	else:
		username = request.args.get('username')
		my_recs = recommender(username)
		recs = list(routes.find({"id": {"$in": list(my_recs['route_id'])}}))
	return render_template('my-recommendations.html', recs=recs)

# Shut down the scheduler when exiting the app
#atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
	# Register for pinging service

	# Connect to the database
	client = MongoClient()
	db = client.routes_updated
	routes = db.routes
	db = client.ratings
	ratings = db.ratings
	db = client.users
	users = db.users

	# Start Flask app
	app.run(host='0.0.0.0', port=PORT, threaded=True, debug=True)
