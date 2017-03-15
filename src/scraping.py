import requests
from bs4 import BeautifulSoup
import time
from urllib import urlencode
import selenium.webdriver
import pandas as pd
import random
from pymongo import MongoClient
import json


def search_mnt_project(url,  browser, delay=3):
    '''Pulls page content and returns it'''
    browser.get(url)
    # make delay more random
    delay = random.randint(2, 6)
    time.sleep(delay)  # Wait a few seconds before getting the HTML source
    return browser.page_source

def soup_maker(url):
    '''Opens up selenium webdriver and returns soup'''
    browser = selenium.webdriver.Firefox()
    html = search_mnt_project(url,browser)
    browser.quit()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def find_table_urls(table_tag, href_list):
    '''
     Pulls route urls from table
    '''
    for t in table_tag:
        for row in t.findAll('tr'):
            stars = row.findAll('td')[1].find('span',{'class': 'small textLight'})
            # stop if not review
            if stars != None:
                if str(stars.text) == ' (0)':
                    continue
            a = row.findAll('td')[0].find('a', href=True)
            if a != None:
                href_list.append(a.get('href'))
    return href_list


def find_route_urls(query, route_href_list):
    '''
    INPUT
        - url - a page url 
        - route_href_list - list of href's for routes
    OUTPUT
        - route_href_list - list of href's for routes
        - soup - the html for the given page
    '''
    url = "https://www.mountainproject.com%s" % query
    soup = soup_maker(url)
    table_tag = soup.select('table.objectList')
    product_tags = soup.select('div.search-result-gridview-item')
    route_href_list = find_table_urls(table_tag, route_href_list)
    return route_href_list, soup


def all_route_urls(start_url):
    '''
    find all route urls
    INPUT
        - start_url - first url to go to
    OUTPUT
        - route_href_list - list off all the route's urls
    '''
    # make empty list to fill with route page urls
    route_href_list = [] 
    route_href_list, soup = find_route_urls(start_url, route_href_list)
    # click next page
    page_url = ''
    while page_url is not None:
        for a in soup.find('td', {'align': 'right'}).findAll('a',href=True):
            if 'Next' in a.text:
                page_url = a.get('href')
                break
            else:
                page_url = False
        if page_url == False:
            page_url = None
            break
        route_href_list, soup = find_route_urls(page_url, route_href_list)
    return route_href_list


def scrape_route_page(query):
    '''
    INPUT
        - query     
    OUTPUT
    
    '''
    url = "https://www.mountainproject.com%s" % query
    soup = soup_maker(url)
    page_tag = soup.find('div', {'id':'rspCol800'})
    # make route dict
    route_dict = {}
    route_dict['name'] = page_tag.find('span', {'itemprop':'itemreviewed'}).text
    route_dict['grade'] = page_tag.find('span', {'class':'rateYDS'}).text
    route_stars_text = soup.find('span', {'id':'starSummaryText'}).text.split('Average: ')
    route_dict['average_rating'] = route_stars_text[1][:3]
    # convert to string from unicode
    star_url = str(soup.find('span', {'id':'starSummaryText'}).find('a', href=True).get('href'))
    
    for i, td in enumerate(page_tag.find('table').findAll('td')): 
        if td.text.split(':')[0] == 'Type':
            route_dict['type'] = page_tag.find('table').findAll('td')[i+1].text
        elif td.text.split(':')[0] == 'Original':
            route_dict['original_grade'] = page_tag.find('table').findAll('td')[i+1].text
        elif td.text.split(':')[0] == 'FA':
            fa = str(page_tag.find('table').findAll('td')[i+1].text)
            route_dict['FA'] = fa
        elif td.text.split(':')[0] == 'Season':
            season = page_tag.find('table').findAll('td')[i+1].text
            route_dict['season'] = season
        elif td.text.split(':')[0] == 'Page Views':
            route_dict['page_views'] = page_tag.find('table').findAll('td')[i+1].text
        elif td.text.split(':')[0] == 'Submitted By':
            route_dict['submitted_by'] = page_tag.find('table').findAll('td')[i+1].text
            
    return star_url, route_dict


def scrape_ratings_by_user(query, route_name):
    rating_dict = {'route_name': route_name, 'username': [], 'rating':[]}
    url = "https://www.mountainproject.com%s" % query
    soup = soup_maker(url)
    table_tag = soup.findAll('table')
    # the 4th table is the one with star votes
    for row in table_tag[3].findAll('tr'):
        for i, column in enumerate(row.findAll('td')):
            if i % 2 == 0:
                rating_dict['username'].append(column.text) # username
                user_url = str(column.find('a', href=True).get('href')) #query for user url
            if i % 2 == 1:
                rating_dict['rating'].append(int(column.text.split('Html(')[1][0]) - 1) # number of stars
    return user_url, rating_dict

def scrape_user(query):
    '''returns user info'''
    url = "https://www.mountainproject.com%s" % query
    soup = soup_maker(url)
    # make user dict
    user_dict = {}
    user_dict['name'] = str(soup.find('h1').text)
    side_bar = soup.select('div.roundedBottom')[0].text.split('\n') # side bar
    user_dict['member_since'] = side_bar[3].split('Since: ')[1]
    user_dict['last_vist'] = side_bar[4].split('Visit: ')[1]
    user_dict['point_rank'] = side_bar[9].split('Rank: # ')[1]
    user_dict['total_points'] = side_bar[10].split('Points: ')[1].replace(',', '')
    user_dict['compliments'] = side_bar[11].split(' Compliments')[0]
    
    for item in soup.find('div',{'class': 'personalData'}).text.split('\n'):
        if 'Personal' in item:
            user_dict['personal'] = item.split('Personal: ')[1]
        elif 'Favorite Climbs:' in item:
            user_dict['favorite_climbs'] = item.split('Favorite Climbs: ')[1]
        elif 'Other Interests:' in item:
            user_dict['other_interests'] = item.split('Other Interests: ')[1]
        elif 'Likes to climb:' in item:
            user_dict['likes_to_climb'] = item.split('Likes to climb: ')[1]
        elif 'Trad:' in item:
            user_dict['trad'] = item.split('Trad:')[1]
        elif 'Sport:' in item:
            user_dict['sport'] = item.split('Sport:')[1]
        elif 'Aid:' in item:
            user_dict['aid'] = item.split('Aid:')[1]
        elif 'Ice:' in item:
            user_dict['ice'] = item.split('Ice:')[1]
    return user_dict

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


def search_route_page(grade)
    query = '''/scripts/Search.php?searchType=routeFinder&minVotes=
    0&selectedIds=105708966&type=rock&diffMinrock={}&diffMinboulder=
    20000&diffMinaid=70000&diffMinice=30000&diffMinmixed=
    50000&diffMaxrock={}&diffMaxboulder=21400&diffMaxaid=
    75260&diffMaxice=38500&diffMaxmixed=60000&is_trad_climb=
    1&is_sport_climb=1&is_top_rope=1&stars=1.8&pitches=0&sort1=
    title&sort2=rating'''.format(*grade)
    return query


if __name__ == "__main__":
    grades = [(800,1600),(1800,2000),(2300,2300),
             (2600,2700),(3100,3300),(4600,5300),
             (6600,12400)]
    for grade in grades:
        query = search_route_page(grade)
    # returns all route urls
    route_urls = all_route_urls(washington_route_url)

    star_urls = []
    for i, quary in enumerate(route_urls):
        star_url, route_dict = scrape_route_page(quary) # updates route_df and return star_url
        add_to_route_database(route_dict)
        user_url, rating_dict = scrape_ratings_by_user(star_url, route_dict['name'])
        add_to_rating_database(rating_dict)
        user_dict = scrape_user(user_url)
        add_to_user_database(user_dict)




