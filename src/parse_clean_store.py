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


