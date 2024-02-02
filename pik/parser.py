import json
import os

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pprint import pprint

agent = UserAgent()

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                     '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
           'User-Agent': agent.random}

base_url = 'https://ooo-pic.ru'
def get_data():
    response = requests.get('https://ooo-pic.ru/', headers=headers)
    bs = BeautifulSoup(response.text, 'lxml')

    # ------------Формируем ссылки на все категории в меню-------------------------

    first_cat_link_list = [[], ]

    cat_list = bs.find(id='menu_b', class_='kategor2').find_all('li', recursive=False)

    tools = cat_list[0].find('ul').find_all('li', recursive=False)

    for i in tools:
        first_cat_link_list[0].append(i.find('a').get('href'))

    for i in cat_list:
        first_cat_link_list.append(i.find('a').get('href'))

    # pprint(first_cat_link_list)

    # ------------итерируемся по полученным категориям верхнего уровня-------------------------
    sub_cat_list = []
    for category in first_cat_link_list:
        # print(category)
        if isinstance(category, list):
            for sub_category in category[:1]:
                # print(base_url+sub_category)
                response = requests.get(base_url+sub_category, headers=headers).text
                # print(response)
                bs = BeautifulSoup(response, 'lxml')
                ul = bs.find('ul', class_='pages-list')
                # print(ul)
                a_list = [i.get('href') for i in ul.find_all('a')]
                # pprint(a_list)

                for item in a_list:
                    response = requests.get(base_url+item, headers=headers).text
                    bs = BeautifulSoup(response, 'lxml')
                    if bs.find('ul', class_='pages-list'):
                        pass
                    else:
                        tables_products = bs.find_all('table', class_='table1')
                        for table in tables_products:
                            row_list = table.find_all('tr')[1:]

def main():
    get_data()


if __name__ == '__main__':
    main()
