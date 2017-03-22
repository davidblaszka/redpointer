import requests
from bs4 import BeautifulSoup
import time
from urllib import urlencode
import pandas as pd
from pymongo import MongoClient


def scrape_route_page(html):
    '''
    Scrapes route pages for html 
    returns soup, url for the rating page for the route, and route name
    '''
    soup = BeautifulSoup(html, 'html.parser')
    # convert to string from unicode
    star_url = str(soup.find('span', {'id': 'starSummaryText'}).\
				find('a', href=True).get('href'))
    page_tag = soup.find('div', {'id': 'rspCol800'})
    route_name = page_tag.find('span', {'itemprop': 'itemreviewed'}).text
    return star_url, html, route_name


def scrape_ratings_by_user(html):
    '''
    Input: query to ratings page and route_name
    Output: user_url, and rating_info
    '''
    rating_dict = {'username': [], 'rating': [], 'user_url': []}
    rating_dict['html'] = html
    soup = BeautifulSoup(html, 'html.parser')
    soup.find('div', {'id': 'navBox'})
    a = soup.find('div', {'id': 'navBox'})
    url = a.findAll('a', href=True)[-1].get('href')
    rating_dict['route_url'] = url
    table_tag = soup.findAll('table')
    # the 4th table is the one with star votes
    for row in table_tag[3].findAll('tr'):
        for i, column in enumerate(row.findAll('td')):
            if i % 2 == 0:
                rating_dict['username'].append(column.text)  # username
                rating_dict['user_url'].append(str(column.find('a', href=True).\
                            get('href')))  # query for user url
            if i % 2 == 1:
                rating_dict['rating'].append(\
                    int(column.text.split('Html(')[1][0]) - 1) # number of stars
    return rating_dict


def add_to_route_database(route_dict):
    client = MongoClient('mongodb://localhost:27017/')
    db = client.routes_collection_updated
    routes_collection = db.routes_collection
    try:
        routes_collection.insert_one(route_dict)
    except:
        print("add_to_route_database error: ", route_dict.keys())


def add_to_rating_database(rating_dict):
    client = MongoClient('mongodb://localhost:27017/')
    db = client.ratings_collection_updated
    ratings_collection = db.ratings_collection
    try:
        ratings_collection.insert_one(rating_dict)
    except:
        print("add_to_rating_database error: ", rating_dict.keys())


if __name__ == "__main__":
    client = MongoClient('mongodb://localhost:27017/')
    db = client.route_url
    route_url = db.route_url
    route_url_dict = route_url.find()
    route_href_list = list(route_url_dict)[0]['route_urls']

    db = client.route_html_collection
    route_html_collection = db.route_html_collection
    raw_data = route_html_collection.find()
    df_route_html = pd.DataFrame(list(raw_data))

    db = client.ratings_info
    ratings_info = db.ratings_info
    raw_data = ratings_info.find()
    ratings_df = pd.DataFrame(list(raw_data))

    for route_url,route_html in zip(df_route_html['html'], route_href_list):
        star_url, route_html, route_name = scrape_route_page(route_html)
        route_html_dict = {'route': route_name, 
                            'html': route_html,
                            'url': route_url}
        add_to_route_database(route_html_dict)

    for ratings_html, route_name in zip(ratings_df['html'], ratings_df['name']):
        rating_dict = scrape_ratings_by_user(ratings_html)
        rating_dict['route'] = route_name
        add_to_rating_database(rating_dict)
