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


def item_by_item_matrix(routes_df):
    '''make item-by-item matrix based on cosine similarity'''
    # load data frame from csv
    routes_id = routes_df['id']
    routes_df_new = routes_df.drop('id', axis=1)
    items_mat = np.array(list(routes_df_new.values)).astype(float)
    # normalize features
    items_mat_norm = normalize(items_mat)
    cos_sim = 1-pairwise_distances(items_mat, metric="cosine")
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
    

def query_routes(routes_df, grade_g, grade_l, climb_type):
    # load data frame from csv
    route_list = find_grade(routes_df, grade_g, grade_l)
    id_list = []
    for r in route_list:
        id_list.append(r['id'])
    routes_df = routes_df[routes_df['id'].isin(id_list)]
    routes_df = check_climb_type(routes_df, climb_type)
    return routes_df
    
    
def find_grade(routes_df, grade_g, grade_l):
    '''find the routes with grades between'''
    # open grades.txt to obtain grades in order
    with open('../data/grades.txt') as f:
        grade_data = f.read()
    grade_list = grade_data.replace('\n','').replace(' ', '').split(',')
    # solve for grade indexing
    if grade_g not in grade_list and grade_l not in grade_list:
        grades_ind = []
    elif grade_g not in grade_list and grade_l in grade_list:
        ind2 = grade_list.index(grade_l)
        grades_ind = grade_list[:ind2]
    elif grade_g in grade_list and grade_l not in grade_list:
        ind1 = grade_list.index(grade_g)
        grades_ind = grade_list[ind1:]
    elif grade_g != '' and grade_l != '':
        ind1 = grade_list.index(grade_g)
        ind2 = grade_list.index(grade_l)
        if ind1 < ind2:
            grades_ind = grade_list[ind1:ind2]
        else:
            grades_ind = grade_list[ind2:ind1]
    elif grade_g != '':
        grades_ind = grade_list[grade_list.index(grade_g):]
    elif grade_l != '':
        grades_ind = grade_list[:grade_list.index(grade_l)]
    else:
        grades_ind = grade_list
    client = MongoClient()
    db = client.routes_updated
    routes = db.routes
    route_list = list(routes.find({'grade': {'$in': grades_ind}}))
    return route_list
    
    
def check_climb_type(routes_df, climb_type):
    '''select by climb type'''
    if climb_type.lower() == 'trad':
        routes_df = routes_df[routes_df['Trad'] == 1]
    elif climb_type.lower() == 'sport':
        routes_df = routes_df[routes_df['Sport'] == 1]
    elif climb_type.lower() == 'ice':
        routes_df = routes_df[routes_df['Ice'] == 1]
    elif climb_type.lower() == 'aid':
        routes_df = routes_df[routes_df['Aid'] == 1]
    elif climb_type.lower() == 'tr':
        routes_df = routes_df[routes_df['TR'] == 1]
    elif climb_type.lower() == '':
        routes_df = routes_df
    return routes_df


def routes_only(routes_df, route_id, routes):
    # compute item-by-item similarity
    cos_sim, route_id_list = item_by_item_matrix(routes_df)
    n = 40
    index = route_id_list.tolist().index(route_id)
    arr = cos_sim[index]
    similar_routes = np.asarray(route_id_list)[arr.argsort()[-(n+1):][::-1][1:]].tolist()
    recs = list(routes.find({"id": {"$in": similar_routes}}))
    return recs


def find_sim_routes(route_name, routes_df, grade_g, grade_l, climb_type):
    '''generates cosine similar routes, and queries results'''
    # load route database
    client = MongoClient()
    db = client.routes_updated
    routes = db.routes
    route_id = list(routes.find({'name': route_name}))[0]['id']
    # find similar routes
    recs = routes_only(routes_df, route_id, routes)
    # query results
    routes_df = query_routes(pd.DataFrame(recs), 
                            grade_g, 
                            grade_l, 
                            climb_type)
    routes_df = routes_df.reset_index().drop('index', axis=1)
    routes_df = routes_df.sort_values('average_rating', 
                                        ascending=False).head(20)
    # return to dict format
    recs = routes_df.to_dict(orient='records')
    return recs


def sort_recs(recs):
    '''sort recs to page view'''
    df = pd.DataFrame(recs)
    df = df.sort_values('page_views', ascending=False)
    return df.to_dict(orient='records')


def find_recs(routes_df, grade_g, grade_l, climb_type, user_name):
    '''generates recommendation based on ensemble model'''
    # query routes
    client = MongoClient()
    db = client.routes_updated
    routes = db.routes
    routes_df = query_routes(routes_df, grade_g, grade_l, climb_type)
    routes_df = routes_df.reset_index().drop('index', axis=1)
    user_df, user_id = get_user_info(user_name)
    # make user dataframe
    ratings_data = pd.DataFrame(columns=['route_id', 'user_id'])
    ratings_data['user_id'] = (0 * routes_df['id']) + user_id 
    ratings_data['route_id'] = routes_df['id']
    # find recs from ensemble model
    if ratings_data.empty:
        return []
    else:
        recs_df = ensemble(ratings_data, routes_df, user_df)
        recs_df = recs_df.sort_values('final_pred', ascending=False).head(20)
        recs = list(routes.find({"id": {"$in": list(recs_df['route_id'])}}))
        recs = sort_recs(recs)
        return recs


def recommender(user_name, route_name, grade_g, grade_l, climb_type):
    '''given a username, returns top 6 recommendations'''
    routes_df = pd.read_csv("../data/routes_df.csv", 
                            sep='\t').drop('Unnamed: 0', axis=1)
    # make a dataframe with all the routes and only the user_id
    client = MongoClient()
    db = client.users
    users = db.users
    if user_name == '' and route_name != '':
        recs = find_sim_routes(route_name, 
                                routes_df, 
                                grade_g, 
                                grade_l, 
                                climb_type)
    elif user_name != '' and users.find({'name': user_name}).count()!=0:
        recs = find_recs(routes_df, 
                        grade_g, 
                        grade_l, 
                        climb_type, 
                        user_name)
    else:
        recs = []
    return recs