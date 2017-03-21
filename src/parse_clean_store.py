import requests
from bs4 import BeautifulSoup
import time
from urllib import urlencode
import selenium.webdriver
import random
import pandas as pd
import numpy as np

def parse_route_page(_id, html):
    '''
    takes a soup to parse
    returns dict of route info
    '''
    soup = BeautifulSoup(html, 'html.parser')
    page_tag = soup.find('div', {'id':'rspCol800'})
    # make route dict
    route_dict = {}
    # make id
    route_dict['id'] = _id
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
	'''cleans and sorts FA'''
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


def parse_user(html, _id):
	'''returns user info'''
	soup = BeautifulSoup(html, 'html.parser')
	# make user dict
	user_dict = {'Personal:': np.nan,
					'Favorite Climbs:': np.nan,
					'Other Interests:': np.nan,
					'Likes to climb:': np.nan,
					'Trad:': np.nan,
					'Sport:': np.nan,
					'Aid:': np.nan,
					'Ice:': np.nan}
	
	# make id
	user_dict['id'] = _id
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


def parse_clean_user(html, _id):
	'''returns user info'''
	soup = BeautifulSoup(html, 'html.parser')
	# make user dict
	user_dict = {'Favorite Climbs:': np.nan,
					'Other Interests:': np.nan}

	for item in soup.find('div',{'class': 'personalData'}).text.split('\n'):
		for item2 in user_dict.keys():
			if item2 in item:
				item_list = item.split(item2)
				if len(item_list) > 1:
					user_dict[item2] = item_list[1]
		user_dict = check_climb_types(item, user_dict)
		user_dict = check_personal(item, user_dict)
		user_dict = clean_likes_to_climb(item, user_dict)
	# make id
	user_dict['id'] = _id
	# get username
	user_dict['name'] = soup.find('h1').text.encode('utf-8')

	side_bar = soup.select('div.roundedBottom')[0].text.split('\n') # side bar
	user_dict = clean_points_visits(side_bar, user_dict)
	user_dict =  clean_compliments(side_bar[11], user_dict)
	return user_dict

def clean_points_visits(tag, user_dict):
	'''cleans left bar'''
	user_list = ['Since: ', 'Visit: ', 'Rank: # ', 'Points: ', ' Compliments']
	labels = ['member_since', 'last_vist', 'point_rank', 'total_points']
	for item1 in tag:
		for item2, key in zip(user_list, labels):
			if item2 in item1:
				item_list = item1.split(item2)
				if len(item_list) > 1:
					if key in ['point_rank', 'total_points']:
						points = item_list[1].replace(',', '')
						if points == '-none-':
							user_dict[key] = np.nan
						else:
							user_dict[key] = int(points)
					else:	
						user_dict[key] = item_list[1]
	return user_dict

def clean_compliments(tag, user_dict):
	'''turns compliments into ints'''
	compliments = tag.split(' Compliments')[0]
	compliments = compliments.replace(',' , '')
	if compliments == '':
		compliments = 0
	user_dict['compliments'] = int(compliments)
	return user_dict


def clean_likes_to_climb(item, user_dict):
	'''finds what climbing styles the user likes'''
	climb_list = ['Trad', 'Sport', 'TR', 'Gym']
	key_list = ['likes_trad', 'likes_sport', 'likes_tr', 'likes_gym']
	item2 = 'Likes to climb:'
	if item2 in item:
		item_list = item.split(item2)
		for key, item2 in zip(key_list, climb_list):
			if len(item_list) > 1:
					if item2 in item_list[1]:
						user_dict[key] = 1
					else:
						user_dict[key] = 0
			else:
				user_dict[key] = 0
	return user_dict


def check_personal(item, user_dict):
	'''get city, state, age, and sex'''
	if 'Personal:' in item:
		item_list = item.split('Personal:')
		if len(item_list) > 1:
			if 'Lives in' in item_list[1]:
				personal_list = item_list[1].replace('Lives in', '').split(',')
				city = personal_list[0].encode('utf-8')
				user_dict['city'] = city
				if len(personal_list) > 1:
					state = personal_list[1].encode('utf-8')
					user_dict['state'] = state
				if 'years old' in item_list[1]:
					age = item_list[1].split(' years old')[0]
					age = int(age[::-1][0:2])
					user_dict['age'] = age
				if 'Female' in item_list[1]:
					user_dict['Female'] = 1
				else:
					user_dict['Female'] = 0
		else:
			user_dict['city'] = np.nan
			user_dict['state'] = np.nan
			user_dict['age'] = np.nan
			user_dict['Female'] = np.nan

	return user_dict


def check_climb_types(item, user_dict):
	'''fills user_dict with climbing types'''
	climb_type_list = ['Trad:', 'Sport:', 'Aid:', 'Ice:']
	key_list = [('trad_lead', 'trad_follows'),
				('sport_lead', 'sport_follows'), 
				('aid_leads', 'aid_follows'), 
				('ice_leads','ice_follows')]
	for key, item2 in zip(key_list, climb_type_list):
			if item2 in item:
				item_list = item.split(item2)
				if len(item_list) > 1:
					leads, follows = clean_climb_types(item_list[1])
					user_dict[key[0]] = leads
					user_dict[key[1]] = follows
				else:
					user_dict[key[0]] = np.nan
					user_dict[key[1]] = np.nan
	return user_dict


def clean_climb_types(s):
	'''cleans climbing type strings'''
	s_list = s.split("Follows")
	leads_list = s_list[0].encode('utf-8').split('Leads ') 
	if len(leads_list) < 2:
		leads = np.nan
		follows = np.nan
	else:
		leads = leads_list[1].split('\xc2')[0][-3:]
		if len(s_list) > 1:
			follows = s_list[1].encode('utf-8')[-3:]
		else:
			follows_list = np.nan
	return leads, follows


def create_ratings_matrix(df):
	'''creates a ratings matrix with route_id,user_id, and rating'''
	route_id = 0
	row = 0
	username_list = []
	df_new = pd.DataFrame(columns=['route_id','user_id','rating'])
	for route, usernames, ratings in zip(df['route'], 
	                                    df['username'],
	                                    df['rating']):
	    for username, rating in zip(usernames, ratings):
	        if username not in username_list:
	            username_list.append(username)
	        df_new.loc[row,'route_id'] = route_id
	        df_new.loc[row, 'user_id'] = username_list.index(username)
	        df_new.loc[row, 'rating'] = rating
	        row += 1
	    route_id += 1
	return df_new