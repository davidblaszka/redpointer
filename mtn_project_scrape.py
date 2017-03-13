import requests
from bs4 import BeautifulSoup
import time
from urllib import urlencode
import selenium.webdriver


def search_area(query):
    '''
    INPUT: query to search
    OUTPUT: url

    Return the number of jobs on the indeed.com for the search query.
    '''

    url = "https://www.mountainproject.com%s" % query
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    area = soup.find('div', id='viewerLeftNavColContent')
    area_url = []
    for a in area.find_all('a', href=True):
        if a.text != '' and "Browse" not in str(a.text).split():
            # I might want to search each url first and only stop when I'm at a route only page
             area_url.append(str(a['href']))

    return area_url


start = "/v/washington/105708966"
area_urls = search_area(start)


rock_url = 'https://www.mountainproject.com/scripts/Search.php?searchType=routeFinder&minVotes=0&selectedIds=105708966&type=rock&diffMinrock=800&diffMinboulder=20000&diffMinaid=70000&diffMinice=30000&diffMinmixed=50000&diffMaxrock=12400&diffMaxboulder=21400&diffMaxaid=75260&diffMaxice=38500&diffMaxmixed=60000&is_trad_climb=1&is_sport_climb=1&is_top_rope=1&stars=0&pitches=0&sort1=area&sort2=rating'

def search_table(url):
    '''
    INPUT: query to search
    OUTPUT: url

    Return the number of jobs on the indeed.com for the search query.
    '''
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', id='rspBodyContainer')
    routes = table.find('p')
    for a in routes.find_all('a', href=True):
        if a.text != '' and "Browse" not in str(a.text).split():
            # I might want to search each url first and only stop when I'm at a route only page
             area_url.append(str(a['href']))

    return area_url


def search_mtn_project(url, delay=5):
    browser = selenium.webdriver.Firefox()
    browser.get(url)
    time.sleep(delay)  # Wait a few seconds before getting the HTML source
    return browser.page_source


def route_urls():
    html = search_mnt_project(url)
    soup = BeautifulSoup(html, 'html.parser')
    table_tag = soup.select('table.objectList')
    product_tags = soup.select('div.search-result-gridview-item')

    href_list = []
    for t in table_tag:
        for row in t.findAll('tr'):
            a = row.findAll('td')[0].find('a', href=True)
                if a != None:
                    href_list.append(a.get('href'))
    return href_list

def route_page_info(query):
    url = "https://www.mountainproject.com%s" % query
    html = search_mnt_project(url)
    soup = BeautifulSoup(html, 'html.parser')
    page_tag = soup.find('div', {'id':'rspCol800'})
    route_name = page_tag.find('span', {'itemprop':'itemreviewed'}).text
    route_grade = page_tag.find('span', {'class':'rateYDS'}).text
    # need to find how to extract
    route_stars = str(page_tag.find('span', {'id':'starSummaryText'}).find("meta", {"itemprop" : "average"}))[15:18] # this could be improved
    #star_lurl =

    route_type = page_tag.find('table').findAll('td')[1].text
    route_original_grade = page_tag.find('table').findAll('td')[3].text
    route_FA = page_tag.find('table').findAll('td')[5].text
    route_page_views = page_tag.find('table').findAll('td')[7].text
    route_submitted_by = page_tag.find('table').findAll('td')[9].text

    # maybe grab the rest of the page content for future use


