import requests
from bs4 import BeautifulSoup
import time
from urllib import urlencode
import selenium.webdriver
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


def all_route_urls(query, route_href_list):
    '''
    find all route urls
    INPUT
        - query - first url to go to
    OUTPUT
        - route_href_list - list off all the route's urls
    '''
    route_href_list, soup = find_route_urls(query, route_href_list)
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