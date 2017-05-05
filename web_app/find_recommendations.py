import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine
from pymongo import MongoClient


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
    route_list = find_grade(routes_df, grade_g, grade_l)
    id_list = []
    for r in route_list:
        id_list.append(r['id'])
    routes_df = routes_df[routes_df['id'].isin(id_list)]
    if climb_type != 'Select':
        routes_df = routes_df = routes_df[routes_df[climb_type] == 1]
    return routes_df
    
    
def find_grade(routes_df, grade_g, grade_l):
    '''find the routes with grades between grade_g and grade_l'''
    # open grades.txt to obtain grades in order
    with open('../data/grades.txt') as f:
        grade_data = f.read()
    grade_list = grade_data.replace('\n', '').replace(' ', '').split(',')
    # solve for grade indexing
    if grade_g == 'Select' and grade_l == 'Select':
        grades_ind = grade_list
    elif grade_g == 'Select' and grade_l != 'Select':
        ind2 = grade_list.index(grade_l)
        grades_ind = grade_list[:ind2]
    elif grade_g != 'Select' and grade_l == 'Select':
        ind1 = grade_list.index(grade_g)
        grades_ind = grade_list[ind1:]
    else:
        ind1 = grade_list.index(grade_g)
        ind2 = grade_list.index(grade_l)
        if ind1 < ind2:
            grades_ind = grade_list[ind1:ind2]
        else:
            grades_ind = grade_list[ind2:ind1]
    client = MongoClient()
    db = client.routes_updated
    routes = db.routes
    route_list = list(routes.find({'grade': {'$in': grades_ind}}))
    return route_list
    

def routes_only(routes_df, route_id, routes):
    # compute item-by-item similarity
    cos_sim, route_id_list = item_by_item_matrix(routes_df)
    # select 100 routes for similarity
    n = 100
    index = route_id_list.tolist().index(route_id)
    arr = cos_sim[index]
    similar_routes = np.asarray(route_id_list)[arr.argsort()[-(n+1):][::-1][1:]].tolist()
    recs = list(routes.find({"id": {"$in": similar_routes}}))
    return recs


def find_sim_routes(route_name, routes_df, grade_g, grade_l, climb_type):
    '''generates cosine similar routes, and queries results'''
    # load route database
    client = MongoClient()
    db = client.redpointer
    routes = db.routes
    if list(routes.find({'name': route_name})) == []:
        return []
    route_id = list(routes.find({'name': route_name}))[0]['id']
    # find similar routes
    recs = routes_only(routes_df, route_id, routes)
    # query results
    routes_df = query_routes(pd.DataFrame(recs), 
                            grade_g, 
                            grade_l, 
                            climb_type)
    routes_df = routes_df.reset_index().drop('index', axis=1)
    # sort routes and limit to 20
    routes_df = routes_df.sort_values('average_rating', 
                                        ascending=False).head(20)
    # return to dict format
    recs = routes_df.to_dict(orient='records')
    return recs


def sort_recs(recs):
    '''sort recs to page view'''
    df = pd.DataFrame(recs)
    # sort by page_views in desc order
    df = df.sort_values('page_views', ascending=False)
    # return as dict
    return df.to_dict(orient='records')


def find_recs(routes_df, grade_g, grade_l, climb_type, user_name):
    '''generates recommendation based on ensemble model'''
    # query routes based on inputs
    client = MongoClient()
    db = client.redpointer
    routes = db.routes
    routes_df = query_routes(routes_df, grade_g, grade_l, climb_type)
    # rest index and drop index column
    routes_df = routes_df.reset_index().drop('index', axis=1)
    user_df, user_id = get_user_info(user_name)
    # get recs from user
    user_rec = list(db.user_recs.find({'name': user_name}))
    recs_df = pd.DataFrame(columns = ['route_id'])
    recs_df['route_id'] = user_rec[0]['recs']
    # find interection of recs with query results
    recs_queried_df = recs_df[recs_df['route_id'].isin(routes_df['id'])].head(20)
    recs = list(routes.find({"id": {"$in": recs_queried_df['route_id'].tolist()}}))
    recs = sort_recs(recs)
    return recs


def recommender(user_name, route_name, grade_g, grade_l, climb_type):
    '''given a username, returns top 6 recommendations'''
    routes_df = pd.read_csv("../data/routes_df.csv", 
                            sep='\t').drop('Unnamed: 0', axis=1)
    # make a dataframe with all the routes and only the user_id
    client = MongoClient()
    db = client.redpointer
    users = db.users
    if user_name == '' and route_name != '':
        recs = find_sim_routes(route_name, 
                                routes_df, 
                                grade_g, 
                                grade_l, 
                                climb_type)
    elif user_name != '' and users.find({'name': user_name}).count() !=0:
        recs = find_recs(routes_df, 
                        grade_g, 
                        grade_l, 
                        climb_type, 
                        user_name)
    else:
        recs = []
    return recs
