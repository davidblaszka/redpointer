import requests
from bs4 import BeautifulSoup
import time
from urllib import urlencode
import selenium.webdriver
import random
from pymongo import MongoClient
import json
import boto3
import pandas as pd
from parse_clean_store import (parse_route_page, parse_user)
from bs4 import BeautifulSoup
from matrix_recommender_prep import (clean_ratings, cold_start)

client = MongoClient('mongodb://localhost:27017/')
db = client.route_html_collection
route_html_collection = db.route_html_collection
raw_data = route_html_collection.find()
df_route_html = pd.DataFrame(list(raw_data))
df_route_html.head()

dict_list = []
for _id, html in enumerate(df_route_html['html']):
    dict_list.append(parse_route_page(_id, html))

db = client.routes
routes = db.routes
routes.insert_many(dict_list)

