import requests
from bs4 import BeautifulSoup
import time
from urllib import urlencode
import selenium.webdriver
import random
from pymongo import MongoClient
import json
from route_url_scraper import search_route_page
from route_url_scraper import all_route_urls 
from route_url_scraper import scrape_route_page
from route_url_scraper import scrape_ratings_by_user
from route_url_scraper import scrape_user
from store_in_database import add_to_route_soup
from store_in_database import add_to_rating_database
from store_in_database import add_to_user_soup


if __name__ == "__main__":
	# define grade search tuples 
    grades = [(800,1600), (1800,2000), (2300,2300), 
             (2600,2700), (3100,3300), (4600,5300), 
             (6600,12400)]
    # make empty list to fill with route page urls
    route_href_list = [] 
    for grade in grades:
        query = search_route_page(grade)
    	# returns all route urls
    	route_href_list = all_route_urls(query, route_href_list)
    # save link to database
    add_route_link_database({'route_urls': route_href_list})
    # get html from route page ande user page, and make rating_dict
    for route_href in route_href_list:
    	star_url, route_soup, route_name = scrape_route_page(route_href)
    	route_soup_dict = {route_name: route_soup}
    	add_to_route_soup(route_soup_dict)
    	user_url, rating_dict = scrape_ratings_by_user(star_url, route_name)
    	add_to_rating_database(rating_dict)
    	user_soup, user_name = scrape_user(user_url)
    	user_soup_dict = {user_name: user_soup}
    	add_to_user_soup(user_soup_dict)