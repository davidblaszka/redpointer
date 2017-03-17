import pyspark
from pyspark.sql.types import *
from pyspark.ml.tuning import TrainValidationSplit
from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.ml.evaluation import RegressionEvaluator
from pymongo import MongoClient
import pandas as pd
from matrix_recommender_prep import (clean_ratings, cold_start, update_df)
import numpy as np


def get_route_list():
	client = MongoClient('mongodb://localhost:27017/')
	db = client.ratings_collection
	ratings_collection = db.ratings_collection
	collection = ratings_collection.find({"route": {'$exists' : True }})
	route_list = [d['route'].encode('utf-8').lower() for d in list(collection)]
	return route_list

def find_routes_in_list(routes, ratings):
    route_list = get_route_list()
    # drop caps
    routes = routes
    routes_numeric = []
    for route in routes:
        if route.lower() not in route_list:
            # remove from ratings and routes
            ratings.pop(routes.index(route))
            routes.remove(route)
        else:
            routes_numeric.append(route_list.index(route.lower()))
    return routes_numeric, ratings

def build_dataframe(routes, ratings):
    routes, ratings = find_routes_in_list(routes, ratings)
    # make up username
    data = [(66666, route, rating) for route, rating in zip(routes, ratings)]
    columns = ('username', 'route', 'rating')
    return spark.createDataFrame(data, columns)

def recommend_routes(predict_df):
	path = '/home/david/work/project/Rock-Climbing-Route-Recommender/src/alsmodel'
	recommender = ALSModel.load(path)
	recommender.transform(predict_df)


# Build our Spark Session and Context
spark = pyspark.sql.SparkSession.builder.getOrCreate()
sc = spark.sparkContext
spark, sc

