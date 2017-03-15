from pymongo import MongoClient
import json

def add_route_link_database(route_urls):
	client = MongoClient('mongodb://localhost:27017/')
	db = client.route_urls_collection
	route_urls_collection = db.route_urls_collection
	route_urls_collection.insert_one(route_urls)


def add_to_route_html_database(route_html):
	client = MongoClient('mongodb://localhost:27017/')
	db = client.route_html_collection
	route_html_collection = db.route_html_collection
	try:
		route_html_collection.insert_one(route_html)
	except:
		print("add_to_route_html_database error: ", route_html.keys())


def add_to_user_html_database(user_html):
	client = MongoClient('mongodb://localhost:27017/')
	db = client.user_html_collection
	user_html_collection = db.user_html_collection
	try:
		user_html_collection.insert_one(user_html)
	except:
		print("add_to_user_html_database error: ", user_html.keys())


def add_to_route_database(route_dict):
	client = MongoClient('mongodb://localhost:27017/')
	db = client.routes_collection
	routes_collection = db.routes_collection
	try:
		routes_collection.insert_one(route_dict)
	except:
		print("add_to_route_database error: ", route_dict.keys())


def add_to_rating_database(rating_dict):
	client = MongoClient('mongodb://localhost:27017/')
	db = client.ratings_collection
	ratings_collection = db.ratings_collection
	try:
		ratings_collection.insert_one(rating_dict)
	except:
		print("add_to_rating_database error: ", rating_dict.keys())


def add_to_user_database(user_dict):
	client = MongoClient('mongodb://localhost:27017/')
	db = client.users_collection
	users_collection = db.users_collection
	try:
		users_collection.insert_one(user_dict)
	except:
		print("add_to_user_database error: ", user_dict.keys())