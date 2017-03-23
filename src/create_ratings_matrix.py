from pymongo import MongoClient
import pandas as pd
import json
import numpy as np


def dataframe_from_collection(collection):
	'''covnert mongodb dataframe to pandas dataframe'''
	raw_data = collection.find()
	return pd.DataFrame(list(raw_data))


def create_utility_matrix(df_ratings, df_users, df_routes):
	'''creates a ratings matrix with route_id,user_id, and rating'''
	row = 0
	df_new = pd.DataFrame(columns=['route_id','user_id','rating'])
	for route, usernames, ratings in zip(df_ratings['route'], 
										df_ratings['username'],
										df_ratings['rating']):
		# match route_id
		route_id = df_routes[df_routes['name'] == route]['id'].values
		# skip routes that have same name until given other info
		if len(route_id) > 1:
			continue
		route_id = int(route_id)
		for username, rating in zip(usernames, ratings):
			df_new.loc[row,'route_id'] = route_id
			# clean user_id to match
			username =  username.encode('utf-8')
			username = username.replace('\xc2\xa0', '').decode('utf-8')
			user_id = df_users[df_users['name'] == username]['id'].values
			if len(user_id) < 1:
				continue
			user_id = int(user_id)
			df_new.loc[row, 'user_id'] = user_id
			df_new.loc[row, 'rating'] = rating
	        row += 1
	return df_new

def create_ratings_matrix(df):
	'''creates a ratings matrix with route_id,user_id, and rating'''
	route_id = 0
	row = 0
	username_list = []
	df_new = pd.DataFrame(columns=['route_id',
									'user_id',
									'rating', 
									'route', 
									'username'])
	for route, usernames, ratings in zip(df['route'], 
	                                    df['username'],
	                                    df['rating']):
	    for username, rating in zip(usernames, ratings):
	        if username not in username_list:
	            username_list.append(username)
	        df_new.loc[row,'route_id'] = route_id
	        df_new.loc[row,'route'] = route
	        df_new.loc[row,'username'] = username
	        df_new.loc[row, 'user_id'] = username_list.index(username)
	        df_new.loc[row, 'rating'] = rating
	        row += 1
	    route_id += 1
	return df_new


if __name__ == "__main__":
	client = MongoClient('mongodb://localhost:27017/')
	db = client.ratings_collection
	ratings_df = dataframe_from_collection(db.ratings_collection)

	db = client.users
	df_users = dataframe_from_collection(db.users)
	users_df = df_users[['name', 'id']]

	db = client.routes
	df_routes = dataframe_from_collection(db.routes)
	routes_df = df_routes[['name', 'id']]

	# create utility matrix
	df = create_utility_matrix(ratings_df, users_df, routes_df)

	# save to database
	db = client.utility_matrix
	for d in df.to_dict(orient='record'):
		db.utility_matrix.insert_one(d)
