import requests
from bs4 import BeautifulSoup


def from_url_return_soup(url):
    headers = {'Accept-Language': 'en',
               'X-FORWARDED-FOR': '2.21.184.0'}
    if url[0] == 'i':
        url = 'https://www.' + url
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, features='lxml')
        return soup
    else:
        print('Status code != 200')
