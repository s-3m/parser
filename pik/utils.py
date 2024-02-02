import requests.utils
from bs4 import BeautifulSoup
import os


def get_tool_data(link, headers=None):
    response = requests.get(link, headers=headers).text
    bs = BeautifulSoup(response, 'lxml')
    items_tables = bs.find_all('table', class_='table1')
    if items_tables:
        path_category = bs.find(class_='site-path').text
        category_list = [i.strip() for i in path_category.split('\\')][1:]
        folder_path = f"../{'\\'.join(category_list)}"
        os.makedirs(folder_path, exist_ok=True)
        for table in items_tables:
            tab_heads = table.find_all('td', {'style': 'background-color: #dcdcdc'})
            print(tab_heads)

