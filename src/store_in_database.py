from pymongo import MongoClient
import json

def add_route_link_database(route_urls):
	client = MongoClient('mongodb://localhost:27017/')
	db = client.route_url
	route_url = db.route_url
	route_url.insert_one(route_urls)


def add_to_route_soup(route_soup):
	client = MongoClient('mongodb://localhost:27017/')
	db = client.route_html
	route_html = db.route_html
	route_html.insert_one(route_soup)


def add_to_user_soup(user_soup):
	client = MongoClient('mongodb://localhost:27017/')
	db = client.user_html
	user_html = db.user_html
	user_html.insert_one(route_soup)


def add_to_route_database(route_dict):
	client = MongoClient('mongodb://localhost:27017/')
	db = client.routes
	routes = db.routes
	routes.insert_one(route_dict)


def add_to_rating_database(rating_dict):
	client = MongoClient('mongodb://localhost:27017/')
	db = client.ratings
	ratings = db.ratings
	ratings.insert_one(rating_dict)


def add_to_user_database(user_dict):
	client = MongoClient('mongodb://localhost:27017/')
	db = client.users
	users = db.users
	users.insert_one(user_dict)