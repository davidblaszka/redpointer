import requests
from bs4 import BeautifulSoup
import time
from urllib import urlencode
import selenium.webdriver
import random

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
            route_type = clean_route_type(page_tag.find('table').findAll('td')[i+1])
            route_dict['route_type_list'] = route_type[0]
            route_dict['pitches'] = route_type[1]
            route_dict['height'] = route_type[2]
            route_dict['uiaa'] = route_type[3]
            route_dict['misc'] = route_type[4]
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
	fa_date = float('nan')
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
	list_of_types = ['Trad', 'Sport', 'TR', 'Alpine', 
					'Ice', 'Boulder', 'Aid', 'Mixed']
	# initialize variables
	route_type_list = []
	pitches = float('nan')
	height = float('nan')
	uiaa = float('nan')
	misc = float('nan')
	for item in route_type:
		if item in list_of_types:
			route_type_list.append(item)
		elif 'pitches' in item:
			pitches = item.replace(' pitches', '')
		elif 'pitch' in item:
			pitches = item.replace(' pitch','')
		elif "'" in item:
			height = float(item.replace("'",''))
		elif 'Grade' in item:
			uiaa = item
		else:
			misc = item

	return route_type_list, pitches, height, uiaa, misc


def clean_submitted_by(tag):
	sb = page_tag.text
	sb = sb.encode('utf-8').split(' on ')
	return sb[0], sb[1]


def clean_original_grade(tag):
	grade = page_tag.text
	grade = grade.encode('utf-8').split('\xa0')[1]
	grade = grade.split('French')[0]
	return grade


def clean_grade(tag):
	grade = page_tag.find('span', {'class':'rateYDS'}).text
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