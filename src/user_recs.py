import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
import numpy as np
import pyspark
from pyspark.sql.types import *
from pyspark.ml.recommendation import ALSModel
from sklearn.externals import joblib
from sklearn.preprocessing import normalize
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine
from pymongo import MongoClient


def als_model(data):
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


def item_by_item_matrix(routes_df):
    '''make item-by-item matrix based on cosine similarity'''
    # load data frame from csv
    routes_id = routes_df['id']
    routes_df_new = routes_df.drop('id', axis=1)
    items_mat = np.array(list(routes_df_new.values)).astype(float)
    # normalize features
    items_mat_norm = normalize(items_mat)
    cos_sim = 1 - pairwise_distances(items_mat, metric="cosine")
    return cos_sim, routes_id


def item_by_item(ratings_data, cos_sim, routes_id):
    '''use 5 most similiar route's ratigns to make prediction'''
    # load all routes
    client = MongoClient()
    db = client.routes_updated
    routes = db.routes
    item_by_item_pred = [] 
    n = 5
    for _id in ratings_data['route_id']:
        # find the similar routes
        index = routes_id[routes_id == _id].index.tolist()[0]
        arr = cos_sim[index]
        similar_routes = np.asarray(routes_id)[arr.argsort()[-(n+1):][::-1][1:]]
        # average the five routes together to get rating
        routes_info = list(routes.find({'id':{'$in': similar_routes.tolist()}}))
        pred = []
        for route in routes_info:
            pred.append(route['average_rating'])
        mean_rating = np.mean(pred)
        item_by_item_pred.append(mean_rating) 
    return item_by_item_pred


def weighted2(als_pred_df, item_by_item_pred, gb_pred_array, routes_df):
    '''get ensemble predictions'''
    predictions_df = als_pred_df
    # load weights
    c = np.load('../data/c.npy')
    # get review count
    normalized_rating_count = routes_df['num_reviews'] / \
                                float(routes_df['num_reviews'].max())
    alpha = np.array((2.0 / (1 + np.exp(-c * normalized_rating_count))) - 1)
    beta = np.load('../data/beta.npy')
    predictions_df['weighted'] = alpha *  predictions_df['prediction'] + \
                                (1 - alpha) * np.array(item_by_item_pred)
    predictions_df['final_pred'] = (beta * predictions_df['weighted']) + \
                                ((1 - beta) * pd.DataFrame(gb_pred_array)[0])
    return predictions_df


def ensemble(ratings_data, routes_df, user_df):
    '''ensemble models'''
    # make als_model predictions for the user
    als_pred_df = als_model(ratings_data)
    # get gradient boosted predictions
    gb_pred_array = gradient_boosting(routes_df, user_df)
    # get cos_sim matrix
    cos_sim, routes_id = item_by_item_matrix(routes_df)
    # get item_by_item predictions
    item_by_item_pred = item_by_item(ratings_data, cos_sim, routes_id)
    # get ensemble predictions
    predictions_df = weighted2(als_pred_df, item_by_item_pred, 
                                gb_pred_array, routes_df)
    return predictions_df
    

def get_user_info(user_name):
    # load data frame from csv
    users_df = pd.read_csv("../data/users_df.csv", 
                            sep='\t').drop('Unnamed: 0', axis=1)
    # grab user info
    user_info = users_df[users_df['name'] == user_name]
    user_id = user_info['id'].iloc[0]
    user_df = user_info.reset_index().drop(['index', 'name', 'id'], axis=1)
    return user_df, user_id
    

def find_recs(routes_df, user_name):
    '''generates recommendation based on ensemble model'''
    # query routes
    client = MongoClient()
    db = client.routes_updated
    routes = db.routes
    routes_df = routes_df.reset_index().drop('index', axis=1)
    user_df, user_id = get_user_info(user_name)
    # make user dataframe
    ratings_data = pd.DataFrame(columns=['route_id', 'user_id'])
    ratings_data['user_id'] = (0 * routes_df['id']) + user_id 
    ratings_data['route_id'] = routes_df['id']
    # find recs from ensemble model
    recs_df = ensemble(ratings_data, routes_df, user_df)
    recs_df = recs_df.sort_values('final_pred', ascending=False)
    return recs_df['route_id']


if __name__ == '__main__':
    '''given a username, returns top 6 recommendations'''
    routes_df = pd.read_csv("../data/routes_df.csv", 
                            sep='\t').drop('Unnamed: 0', axis=1)
    # load data frame from csv
    users_df = pd.read_csv("../data/users_df.csv", 
                            sep='\t').drop('Unnamed: 0', axis=1)

    # Build our Spark Session and Context
    spark = pyspark.sql.SparkSession.builder.getOrCreate()
    sc = spark.sparkContext
    spark, sc
    # start mongo client
    client = MongoClient()
    db = client.redpointer

    for name in users_df['name']:
        recs = find_recs(routes_df, name)
        user_rec_dict = {}
        user_rec_dict['recs'] = recs.tolist()
        user_rec_dict['name'] = name
        db.user_recs.insert_one(user_rec_dict)
