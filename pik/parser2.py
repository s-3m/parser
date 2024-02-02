import json
import os

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pprint import pprint
from utils import get_tool_data

agent = UserAgent()

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                     '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
           'User-Agent': agent.random}

base_url = 'https://ooo-pic.ru'


def get_data():
    response = requests.get('https://ooo-pic.ru/', headers=headers)
    bs = BeautifulSoup(response.text, 'lxml')

    all_a = bs.find('nav', class_='kategor-wr').find_all('a')
    all_href = [i.get('href') for i in all_a][:-1]

    # pprint(all_href)

    for link in all_href:
        if not link.startswith('https'):
            link = base_url + link
        print(get_tool_data(link, headers))


def main():
    get_data()


if __name__ == '__main__':
    main()
