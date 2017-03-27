from pymongo import MongoClient
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
import pyspark
from pyspark.sql.types import *
from pyspark.ml.tuning import TrainValidationSplit
from pyspark.ml.recommendation import ALS, ALSModel
from sklearn.externals import joblib
from sklearn.preprocessing import normalize
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine

def als_model(y_train, y_test):
	'''uses sparks als model to predict ratings'''
	# Convert to a Spark DataFrame
	y_train_spark = spark.createDataFrame(y_train)
	y_test_spark = spark.createDataFrame(y_test)
	# make als_model
	path = '../data/alsmodel_val'
	recommender = ALSModel.load(path)
	# Make predictions for the whole test set
	predictions = recommender.transform(y_test_spark)
	return predictions.toPandas()


def gradient_boosting(X_test):
	'''load gradient boosting model'''
	gb = joblib.load('../pickle/gb_model_val.pkl') 
	return gb.predict(X_test)


def item_by_item_matrix():
	'''make item-by-item matrix based on cosine similarity'''
	# load data frame from csv
	routes_df = pd.read_csv("routes_df.csv", sep='\t').drop('Unnamed: 0', axis=1)
	routes_id = routes_df['id']
	routes_df =	routes_df.drop('id', axis=1)
	items_mat = np.array(list(routes_df.values)).astype(float)
	# normalize features
	items_mat_norm = normalize(items_mat)
	cos_sim = 1-pairwise_distances(items_mat, metric="cosine")
	return cos_sim, routes_id


def item_by_item(y_train, y_test, cos_sim, routes_id):
	'''use 5 most similiar route's ratigns to make prediction'''
	item_by_item_pred = [] 
	n = 5
	for _id in y_test['route_id']:
		# find the similar routes
		index = routes_id[routes_id == _id].index.tolist()[0]
		arr = cos_sim[index]
		similar_routes = np.asarray(routes_id)[arr.argsort()[-(n+1):][::-1][1:]]
		# average the five routes together to get rating
		pred = y_train[y_train['route_id'].isin(similar_routes)]['rating']
		mean_rating = pred.mean()
		item_by_item_pred.append(mean_rating) 
	return item_by_item_pred


def weighted(X_test, als_pred_df, item_by_item_pred):
	# get the number of reviews normalized
	normalized_rating_count = X_test['num_reviews'] / float(X_test['num_reviews'].max())
	predictions_df = als_pred_df
	rmse_list = []
	# solve for lowest rmse for weighted item_by_iteem + als_model
	for c in np.linspace(100.0,110.0, 100):
		alpha = np.array((2.0 / (1 + np.exp(-c * normalized_rating_count))) - 1)
		predictions_df['weighted'] = alpha *  predictions_df['prediction'] + (1 - alpha) * item_by_item_pred
		predictions_df['squared_error'] = (predictions_df['rating'] - predictions_df['weighted'])**2
		# Calculate RMSE
		rmse = np.sqrt(sum(predictions_df['squared_error']) / len(predictions_df))
		rmse_list.append(rmse)
	# grab constant that lowers rmse
	c = np.linspace(100.0,110.0, 100)[rmse_list.index(min(rmse_list))]
	# return weights
	alpha = np.array((2.0 / (1 + np.exp(-c * normalized_rating_count))) - 1)
	# save weight
	np.save('../data/c', c)
	return alpha


def weighted2(als_pred_df, alpha, item_by_item_pred, gb_pred_array):
	'''find bestweight for gb model in ensemble'''
	predictions_df = als_pred_df
	# fill nulls with item_by item value
	rmse_list = []
	for beta in np.linspace(0.0, 1.0, 100):
	    predictions_df['weighted'] = alpha *  predictions_df['prediction'] + (1 - alpha) * item_by_item_pred
	    predictions_df['weighted2'] = (beta * predictions_df['weighted']) + ((1 - beta) * pd.DataFrame(gb_pred_array)[0])
	    predictions_df['squared_error'] = (predictions_df['rating'] - predictions_df['weighted2'])**2
	    rmse = np.sqrt(sum(predictions_df['squared_error']) / len(predictions_df))
	    rmse_list.append(rmse)
	beta = np.linspace(0.0, 1.0, 100)[rmse_list.index(min(rmse_list))]
	# save weight
	np.save('../data/beta', beta)
	return predictions_df, min(rmse_list)


def ensemble(y_train, y_test, X_test):
	'''ensemble models'''
	# make als_model predictions
	als_pred_df = als_model(y_train, y_test)
	# get gradient boosted predictions
	gb_pred_array = gradient_boosting(X_test)
	# get cos_sim matrix
	cos_sim, routes_id = item_by_item_matrix()
	# get item_by_item predictions
	item_by_item_pred = item_by_item(y_train, y_test, cos_sim, routes_id)
	# fill nulls in als model with item_by item prediction
	null_ind = pd.isnull(als_pred_df).any(1).nonzero()[0]
	als_pred_df.ix[null_ind, 'prediction'] = np.array(item_by_item_pred)[null_ind]
	# get weight for item by item, als ensemble
	alpha = weighted(X_test, als_pred_df, item_by_item_pred)
	predictions_df, rmse = weighted2(als_pred_df, alpha, item_by_item_pred, gb_pred_array)
	print rmse


if __name__ == '__main__':
	# Build our Spark Session and Context
	spark = pyspark.sql.SparkSession.builder.getOrCreate()
	sc = spark.sparkContext
	spark, sc

	# load data frame from csv
	data_df = pd.read_csv("model_df.csv", sep='\t')
	# drop duplicates
	data_df = data_df.drop_duplicates(subset=['route_id', 'user_id'])
	y_data = data_df[['route_id', 'user_id','rating']]
	x_data = data_df.drop(['rating', 
							'route_id', 
							'user_id', 
							'member_since', 
							'Unnamed: 0'], 
							axis=1)
	X_train, X_test, y_train, y_test = train_test_split(x_data, y_data, random_state=42)
	ensemble(y_train, y_test, X_test)
	