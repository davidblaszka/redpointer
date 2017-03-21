import requests
from bs4 import BeautifulSoup
import time
from urllib import urlencode
import selenium.webdriver
import random


def get_html(url, browser, delay=3):
    '''Pulls page content and returns it'''
    browser.get(url)
    # make delay more random
    #delay = random.randint(2, 6)
    time.sleep(delay)  # Wait a few seconds before getting the HTML source
    return browser.page_source


def find_table_urls(table_tag, href_list):
    '''
     Pulls route urls from table
    '''
    for t in table_tag:
        for row in t.findAll('tr'):
            stars = row.findAll('td')[1].find('span', {'class': 'small textLight'})
            # stop if not review
            if stars is not None:
                if str(stars.text) == ' (0)':
                    continue
            a = row.findAll('td')[0].find('a', href=True)
            if a is not None:
                href_list.append(a.get('href'))
    return href_list


def find_route_urls(query, route_href_list, browser):
    '''
    INPUT
        - url - a page url
        - route_href_list - list of href's for routes
    OUTPUT
        - route_href_list - list of href's for routes
        - soup - the html for the given page
    '''
    url = "https://www.mountainproject.com%s" % query
    html = get_html(url, browser)
    soup = BeautifulSoup(html, 'html.parser')
    table_tag = soup.select('table.objectList')
    product_tags = soup.select('div.search-result-gridview-item')
    route_href_list = find_table_urls(table_tag, route_href_list)
    return route_href_list, soup


def all_route_urls(query, route_href_list, browser):
    '''
    find all route urls
    INPUT
        - query - first url to go to
    OUTPUT
        - route_href_list - list off all the route's urls
    '''
    route_href_list, soup = find_route_urls(query, route_href_list, browser)
    # click next page
    page_url = ''
    while page_url is not None:
        for a in soup.find('td', {'align': 'right'}).\
			findAll('a', href=True):
            if 'Next' in a.text:
                page_url = a.get('href')
                break
            else:
                page_url = False
        if page_url is False:
            page_url = None
            break
        route_href_list, soup = find_route_urls(page_url, route_href_list, browser)
    return route_href_list


def scrape_route_page(query, browser):
    '''
    Scrapes route pages for html 
    returns soup, url for the rating page for the route, and route name
    '''
    url = "https://www.mountainproject.com%s" % query
    html = get_html(url, browser)
    soup = BeautifulSoup(html, 'html.parser')
    # convert to string from unicode
    star_url = str(soup.find('span', {'id': 'starSummaryText'}).\
				find('a', href=True).get('href'))
    page_tag = soup.find('div', {'id': 'rspCol800'})
    route_name = page_tag.find('span', {'itemprop': 'itemreviewed'}).text
    return star_url, html, route_name


def scrape_ratings_by_user(query, browser):
    '''
    Input: query to ratings page and route_name
    Output: user_url, and rating_info
    '''
    rating_dict = {'username': [], 'rating': [], 'user_url': []}
    url = "https://www.mountainproject.com%s" % query
    html = get_html(url, browser)
    rating_dict['html'] = html
    soup = BeautifulSoup(html, 'html.parser')
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


def scrape_user(query, browser):
    '''returns user page html'''
    user_dict = {}
    url = "https://www.mountainproject.com%s" % query
    html = get_html(url, browser)
    soup = BeautifulSoup(html, 'html.parser')
    user_name = str(soup.find('h1').text)
    user_dict['html'] = html
    user_dict['url'] = query
    user_dict['username'] = user_name
    return user_dict


def search_route_page(grade):
    query = '''/scripts/Search.php?searchType=routeFinder&minVotes=
    0&selectedIds=105708966&type=rock&diffMinrock={}&diffMinboulder=
    20000&diffMinaid=70000&diffMinice=30000&diffMinmixed=
    50000&diffMaxrock={}&diffMaxboulder=21400&diffMaxaid=
    75260&diffMaxice=38500&diffMaxmixed=60000&is_trad_climb=
    1&is_sport_climb=1&is_top_rope=1&stars=1.8&pitches=0&sort1=
    title&sort2=rating'''.format(*grade)
    return query

