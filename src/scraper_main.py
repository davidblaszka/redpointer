import requests
from bs4 import BeautifulSoup
import time
from urllib import urlencode
import selenium.webdriver
import random
from pymongo import MongoClient
import json


if __name__ == "__main__":
	# define grade search tuples 
    grades = [(800,1600),(1800,2000),(2300,2300),
             (2600,2700),(3100,3300),(4600,5300),
             (6600,12400)]
    # make empty list to fill with route page urls
    route_href_list = [] 
    for grade in grades:
        query = search_route_page(grade)
    	# returns all route urls
    	route_href_list = all_route_urls(query, route_href_list)
    # save route_href_list to database