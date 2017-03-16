import requests
from bs4 import BeautifulSoup
import time
from urllib import urlencode
import selenium.webdriver
import random
import pandas as pd
import numpy as np

def parse_route_page(html):
    '''
    takes a soup to parse
    returns dict of route info
    '''
    soup = BeautifulSoup(html, 'html.parser')
    page_tag = soup.find('div', {'id':'rspCol800'})
    # make route dict
    route_dict = {}
    name = page_tag.find('span', {'itemprop':'itemreviewed'}).text
    route_dict['name'] = name.encode('utf-8')
    route_dict['grade'] = clean_grade(page_tag)
    route_dict['average_rating'] = clean_average_rating(soup)
    
    for i, td in enumerate(page_tag.find('table').findAll('td')): 
        if td.text.split(':')[0] == 'Type':
            route_type_dict = clean_route_type(page_tag.find('table').findAll('td')[i+1])
            for key, value in zip(route_type_dict.keys(), route_type_dict.values()):
            	route_dict[key] = value
        elif td.text.split(':')[0] == 'Original':
            o_grade = clean_original_grade(page_tag.find('table').findAll('td')[i+1])
            route_dict['original_grade'] = o_grade
        elif td.text.split(':')[0] == 'FA':
            fa = page_tag.find('table').findAll('td')[i+1].text
            route_dict['FA'] = fa
        elif td.text.split(':')[0] == 'Season':
            season = page_tag.find('table').findAll('td')[i+1].text
            route_dict['season'] = season.encode('utf-8')
        elif td.text.split(':')[0] == 'Page Views':
			page_view = page_tag.find('table').findAll('td')[i+1].text
			route_dict['page_views'] = int(page_view.encode('utf-8').replace(',',''))
        elif td.text.split(':')[0] == 'Submitted By':
            sb = clean_submitted_by(page_tag.find('table').findAll('td')[i+1])
            route_dict['submitted_by'] = sb[0]
            route_dict['submitted_on'] = sb[1]

    return route_dict


def clean_first_ascent(tag):
	fa = tag.text.encode('utf-8')
	fa_list = fa.split(',')
	fa_people = []
	fa_date = np.nan
	chars1 = set('?/')
	chars2 = set('?')
	for item in fa_list:
		if not any((c not in chars1) for c in item):
			fa_people.append(item)
		elif any((c not in chars2) for c in item):
			fa_date = item
	return fa_people, fa_date


def clean_route_type(tag):
	route_type = tag.text
	route_type = route_type.encode('utf-8').split(', ')
	# initialize variables
	route_type_dict = {'Trad': 0, 'Sport': 0, 'TR': 0, 'Alpine': 0, 
                'Ice': 0, 'Boulder': 0, 'Aid': 0, 'Mixed': 0, 
                   'pitches': np.nan,'uiaa': np.nan, 
                   'height': np.nan}
	list_of_types = ['Trad', 'Sport', 'TR', 'Alpine', 
	                'Ice', 'Boulder', 'Aid', 'Mixed']
	for item in route_type:
	    for item2 in route_type_dict.keys():
	        if item2 in item and item2 in list_of_types:
	            route_type_dict[item2] = 1 
	        elif 'pitches' in item:
	            route_type_dict['pitches'] = int(item.replace(' pitches', ''))
	        elif 'pitch' in item:
	            route_type_dict['pitches'] = int(item.replace(' pitch',''))
	        elif "'" in item:
	            route_type_dict['height'] = float(item.replace("'",''))
	        elif 'Grade' in item:
	            route_type_dict['uiaa'] = item
	return route_type_dict


def clean_submitted_by(tag):
	sb = tag.text
	sb = sb.encode('utf-8').split(' on ')
	return sb[0], sb[1]


def clean_original_grade(tag):
	grade = tag.text
	grade = grade.encode('utf-8').split('\xa0')[1]
	grade = grade.split('French')[0]
	return grade


def clean_grade(tag):
	grade = tag.find('span', {'class':'rateYDS'}).text
	grade = grade.encode('utf-8').split('\xa0')[1]
	return grade


def clean_average_rating(soup):
	route_stars_text = soup.find('span', {'id':'starSummaryText'}).text.split('Average: ')
	average_rating = route_stars_text[1][:3]
	if 'OK' in average_rating:
		average_rating = 1.0
	elif 's' in average_rating:
		average_rating = float(average_rating[0])
	else:
		average_rating = float(average_rating)
	return average_rating


def parse_user(html):
	'''returns user info'''
	# make user dict
	soup = BeautifulSoup(html, 'html.parser')

	user_dict = {'Personal:': np.nan,
					'Favorite Climbs:': np.nan,
					'Other Interests:': np.nan,
					'Likes to climb:': np.nan,
					'Trad:': np.nan,
					'Sport:': np.nan,
					'Aid:': np.nan,
					'Ice:': np.nan}

	for item in soup.find('div',{'class': 'personalData'}).text.split('\n'):
		for item2 in user_dict.keys():
			if item2 in item:
				item_list = item.split(item2)
				if len(item_list) > 1:
					user_dict[item2] = item_list[1]

	user_dict['name'] = soup.find('h1').text.encode('utf-8')

	side_bar = soup.select('div.roundedBottom')[0].text.split('\n') # side bar
	user_list = ['Since: ', 'Visit: ', 'Rank: # ', 'Points: ', ' Compliments']
	labels = ['member_since', 'last_vist', 'point_rank', 'total_points']
	for item1 in side_bar:
		for item2, key in zip(user_list, labels):
			if item2 in item1:
				item_list = item1.split(item2)
				if len(item_list) > 1:
					user_dict[key] = item_list[1]

	user_dict['compliments'] = side_bar[11].split(' Compliments')[0]
	return user_dict
