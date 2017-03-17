from flask import Flask, url_for, request, render_template, Markup,redirect
from pymongo import MongoClient
import pandas as pd
from datetime import date
import cPickle as pickle
import time
import atexit
from pyspark.ml.recommendation import ALSModel
import pyspark
from pyspark.sql.types import *
import numpy as np

app = Flask(__name__)
PORT = 8080

@app.route('/')
def root():
	# Build a single row DataFrame
	data = pd.DataFrame(columns=['route_id', 'user_id'])
	ratings_df_pd = pd.DataFrame(list(db.ratings.find())).drop("_id", axis=1)
	data['user_id'] = np.ones(ratings_df_pd['route_id'].unique().shape,dtype=int).tolist()
	data['route_id'] = ratings_df_pd['route_id'].unique().tolist()
	one_row_spark_df = spark.createDataFrame(data)

	# predict 
	my_recs = als_model.transform(one_row_spark_df).toPandas()
	my_top_recs = my_recs.sort_values('prediction', ascending=False).head(6)
	top = list(my_top_recs['route_id'])
	recs = list(routes.find({"id": {"$in": list(my_top_recs['route_id'])}}))
	return render_template('index.html', routes=recs)

'''
@app.route('/returning-user', methods=['GET', 'POST'])
def getReturnRatings():
	hikes = db.hikes.find({})
	return render_template('recommender.html', hikes=hikes)


@app.route('/new-user', methods=['GET', 'POST'])
def getNewRatings():
	hikes = db.hikes.find({})
	return render_template('recommender.html', hikes=hikes)


@app.route('/my-recommendations', methods=['POST', 'GET'])
def getRecs():
	hike_id = hike_ider[request.args.get('hike-name')]
	if request.args.get('username') == '':
		my_recs = ic_model.recommend_from_interactions([hike_id], k=5)
		recs = db.hikes.find({"hike_id": {"$in": list(my_recs['hike_id'])}})
	elif db.users.find({'username': request.args.get('username')}).count()==0:
		db.trip_reports.insert({'Creator': request.args.get('username'), 'Date': date.today().strftime("%B %d, %Y"), 'hike_name': request.args.get('hike-name'), 'Text': request.args.get('tripReport'),
                       'author_id': db.users.count()+1, 'hike_id': hike_id, 'Rating': request.args.get('rating')})
		my_recs = ic_model.recommend_from_interactions([hike_id], k=5)
		recs = db.hikes.find({"hike_id": {"$in": list(my_recs['hike_id'])}})
	else:
		user = int(db.users.find_one({'username': request.args.get('username')})['id'])
		db.trip_reports.insert({'Creator': request.args.get('username'), 'Date': date.today().strftime("%B %d, %Y"), 'hike_name': request.args.get('hike-name'), 'Text': request.args.get('tripReport'),
                       'author_id': user, 'hike_id': hike_id, 'Rating': request.args.get('rating')})
		new_instance = pd.DataFrame.from_dict({'hike_id': [hike_id], 'author_id': [user], 'Rating': [int(request.args.get('rating'))]})
		sf = gl.SFrame(new_instance)
		my_recs = fac_model.recommend(users=[user], new_observation_data=sf, k=5)
		recs = db.hikes.find({"hike_id": {"$in": list(my_recs['hike_id'])}})
	return render_template('my-recommendations.html', recs=recs)
'''
# Shut down the scheduler when exiting the app
#atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
	# Register for pinging service

	# Connect to the database
	client = MongoClient()
	db = client.routes
	routes = db.routes
	db = client.ratings
	ratings = db.ratings

	# Build our Spark Session and Context
	spark = pyspark.sql.SparkSession.builder.getOrCreate()
	sc = spark.sparkContext
	spark, sc

	# load model
	path = '/home/david/work/project/Rock-Climbing-Route-Recommender/web_app/alsmodel'
	als_model = ALSModel.load(path)
	# ic_model = gl.load_model('pickle/itemcontrecommender.pkl')

	# Start Flask app
	app.run(host='0.0.0.0', port=PORT, threaded=True, debug=True)
