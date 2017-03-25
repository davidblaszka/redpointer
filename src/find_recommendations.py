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

def als_model(data):
    # Build our Spark Session and Context
    spark = pyspark.sql.SparkSession.builder.getOrCreate()
    sc = spark.sparkContext
    spark, sc

    '''uses sparks als model to predict ratings'''
    # Convert to a Spark DataFrame
    data_spark = spark.createDataFrame(data)
    # get als_model
    path = '../data/alsmodel_final'
    recommender = ALSModel.load(path)
    # Make predictions for the whole test set
    predictions = recommender.transform(data_spark)
    return predictions.toPandas()


def gradient_boosting(routes_df, user_info):
    '''use gradient boosting model to make predictions'''
    gb = joblib.load('../pickle/gb_model_all_data.pkl')
    gb_predictions = []
    for route_id in routes_df['id']:
        df1 = routes_df[routes_df['id'] == route_id]
        df1 = df1.reset_index().drop(['index', 'id'], axis=1)
        df1 = user_info.join(df1).drop('member_since', axis=1)
        gb_predictions.append(gb.predict(df1))
    return gb_predictions


def item_by_item_matrix():
    '''make item-by-item matrix based on cosine similarity'''
    # load data frame from csv
    routes_df = pd.read_csv("routes_df.csv", sep='\t').drop('Unnamed: 0', axis=1)
    routes_id = routes_df['id']
    routes_df = routes_df.drop('id', axis=1)
    items_mat = np.array(list(routes_df.values)).astype(float)
    # normalize features
    items_mat_norm = normalize(items_mat)
    cos_sim = 1-pairwise_distances(items_mat, metric="cosine")
    return cos_sim, routes_id


def item_by_item(y_data, cos_sim, routes_id):
    '''use 5 most similiar route's ratigns to make prediction'''
    item_by_item_pred = [] 
    n = 5
    for _id in y_data['route_id']:
        # find the similar routes
        index = routes_id[routes_id == _id].index.tolist()[0]
        arr = cos_sim[index]
        similar_routes = np.asarray(routes_id)[arr.argsort()[-(n+1):][::-1][1:]]
        # average the five routes together to get rating
        pred = y_data[y_data['route_id'].isin(similar_routes)]['rating']
        mean_rating = pred.mean()
        item_by_item_pred.append(mean_rating) 
    return item_by_item_pred



def weighted2(als_pred_df, alpha, item_by_item_pred, gb_pred_array):
    '''get ensemble predictions'''
    predictions_df = als_pred_df
    # load alpha and beta weights
    alpha = np.load('../data/beta.npy')
    beta = np.load('../data/beta.npy')
    predictions_df['weighted'] = alpha *  predictions_df['prediction'] + (1 - alpha) * item_by_item_pred
    predictions_df['final_pred'] = (beta * predictions_df['weighted']) + ((1 - beta) * pd.DataFrame(gb_pred_array)[0])
    return predictions_df


def ensemble(ratings_data, routes_df, user_df):
    '''ensemble models'''
    # make als_model predictions for the user
    als_pred_df = als_model(ratings_data)
    # get gradient boosted predictions
    gb_pred_array = gradient_boosting(routes_df, user_df)
    # get cos_sim matrix
    cos_sim, routes_id = item_by_item_matrix()
    # get item_by_item predictions
    item_by_item_pred = item_by_item(y_data, cos_sim, routes_id)
    # get ensemble predictions
    predictions_df = weighted2(als_pred_df, alpha, item_by_item_pred, gb_pred_array)
    return predictions_df.head(6)


def get_user_info(user_name):
    # load data frame from csv
    users_df = pd.read_csv("users_df.csv", sep='\t').drop('Unnamed: 0', axis=1)
    # grab user info
    user_info = users_df[users_df['name'] == user_name]
    user_id = user_info['id'].iloc[0]
    user_df = user_info.reset_index().drop(['index', 'name', 'id'], axis=1)
    return user_df, user_id
    

def recommender(user_name):
    '''given a username, returns top 6 recommendations'''
    user_df, user_id = get_user_info(user_name)
    # load data frame from csv
    routes_df = pd.read_csv("routes_df.csv", sep='\t').drop('Unnamed: 0', axis=1)
    # make a dataframe with all the routes and only the user_id
    ratings_data = pd.DataFrame(columns=['route_id', 'user_id'])
    user_id = user_info()
    ratings_data['user_id'] = (0 * routes_df['id']) + user_id 
    ratings_data['route_id'] = routes_df['id']
    recs_df = ensemble(ratings_data, routes_df, user_df)
    return recs_Df

    