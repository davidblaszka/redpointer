import requests
from bs4 import BeautifulSoup
import time
from urllib import urlencode
import selenium.webdriver
import random


def parse_route_page(soup):
    '''
    takes a soup to parse
    returns dict of route info
    '''
    page_tag = soup.find('div', {'id':'rspCol800'})
    # make route dict
    route_dict = {}
    route_dict['name'] = page_tag.find('span', {'itemprop':'itemreviewed'}).text
    route_dict['grade'] = page_tag.find('span', {'class':'rateYDS'}).text
    route_stars_text = soup.find('span', {'id':'starSummaryText'}).text.split('Average: ')
    route_dict['average_rating'] = route_stars_text[1][:3]
    
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
            
    return route_dict


def parse_user(soup):
    '''returns user info'''
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