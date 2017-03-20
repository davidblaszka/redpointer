from pymongo import MongoClient
import json
import pandas as pd
from parse_clean_store import (parse_route_page, parse_user)


# load route_html database
client = MongoClient('mongodb://localhost:27017/')
db = client.route_html_collection
route_html_collection = db.route_html_collection
raw_data = route_html_collection.find()
df_route_html = pd.DataFrame(list(raw_data))
df_route_html.head()

# parse and clean html
dict_list = []
for _id, html in enumerate(df_route_html['html']):
    dict_list.append(parse_route_page(_id, html))

# insert data into mongodb database
db = client.routes
routes = db.routes
routes.insert_many(dict_list)

