from pymongo import MongoClient
import json
import pandas as pd
from parse_clean_store import (parse_route_page, parse_user_page)
from create_ratings_matrix import create_utility_matrix

def dataframe_from_collection(collection):
    '''convert mongodb dataframe to pandas dataframe'''
    raw_data = collection.find()
    return pd.DataFrame(list(raw_data))


def store_parse_routes(client):
	'''calls parsing functions for routes and stores the cleaned database'''
	# make a ratings dataframe
	db = client.ratings_collection
	ratings_df = dataframe_from_collection(db.ratings_collection)
	# make a route dataframe
	db = client.route_html_collection
	routes_collection = db.route_html_collection
	raw_data = routes_collection.find()
	route_df = pd.DataFrame(list(raw_data))
	# parse and clean route info
	dict_list = []
	# route_df['url'] is off so update from ratings_df
	for _id, (html, route_url) in enumerate(zip(route_df['html'], ratings_df['route_url'])):
	    route_dict = parse_route_page(_id, html)
	    route_dict['route_url'] = route_url
	    dict_list.append(route_dict)
	# store route database
	db = client.routes_updated
	routes = db.routes
	routes.insert_many(dict_list)


def store_parse_users(client):
	'''calls parsing functions for users and stores the cleaned database'''
	db = client.user_html_collection
	users_info = db.user_html_collection
	raw_data = users_info.find()
	df_user_html = pd.DataFrame(list(raw_data))
	# parse and store
	db = client.users
	users = db.users
	_id = 0
	for html in df_user_html['html']:
	    dict_list = parse_user_page(html, _id)
	    users.insert_one(dict_list)
	    _id += 1
	

if __name__ == "__main__":
	client = MongoClient('mongodb://localhost:27017/')
	# parse and store route info
	store_parse_routes(client)
	# parse and store user info
	store_parse_users(client)