import json

import requests.utils
from bs4 import BeautifulSoup
import os
from slugify import slugify
from selenium import webdriver
from requests_html import HTMLSession


def get_tool_data(link, headers=None):
    # response = requests.get(link, headers=headers).text
    # browser = webdriver.ChromiumEdge()
    # browser.get(link)
    # response = browser.page_source
    session = HTMLSession()
    response = session.get(link, headers=headers)
    response.html.render()
    bs = BeautifulSoup(response.html.raw_html, 'lxml')
    items_tables = bs.find_all('table', class_='table1')
    if items_tables:
        path_category = bs.find(class_='site-path').text
        category_list = [i.strip() for i in path_category.split('\\')][1:]
        folder_path = f"../{'\\'.join(category_list)}"
        img_path = f'{folder_path}/img'
        os.makedirs(img_path, exist_ok=True)
        ready_data_for_json = []
        for table in items_tables:
            rowspan = 0
            row_img = None
            tab_heads = table.find_all('td', style=lambda x: x and 'background-color: #dcdcdc;' in x)
            # tab_head_list = [head.text.strip() for head in tab_heads if head.text][:-4]
            product_rows = tab_heads[0].find_parent('tr').find_next_siblings('tr')
            product_rows_list = [i for i in product_rows if len(i) > 5]
            for row in product_rows_list:
                tab_head_list = [head.text.strip().replace('\n\t\t\t', ' ').replace(' ', ' ') for head in tab_heads if
                                 head.text.strip() != '' and head.text.strip()[0].isalpha()]
                row_td = row.find_all('td')
                bs_self_category = row_td[0].find_previous_siblings('td', style=lambda
                    x: x and 'background-color: rgb(135, 206, 250);' in x)
                self_category = bs_self_category[-1].text if bs_self_category else ''
                product_data = []

                img_name = slugify(row_td[0].text.strip())
                img_src = row.find('a', class_='highslide')
                if img_src:
                    img_link = f'https://ooo-pic.ru{img_src.get('href')}'
                    img = requests.get(img_link).content
                    row_img = img

                tool_page = session.get(row_td[0].find('a').get('href'))
                tool_page.html.render()
                bs_tool = BeautifulSoup(tool_page.html.raw_html, 'lxml')
                manufield = bs_tool.find('tr', class_='even').find('td').text

                for i in range(len(row_td) - 1):

                    if len(row_td[3:]) < len(tab_head_list) - 3:
                        tab_head_list = ['Артикул', 'Фото', 'Модель']
                        for z in range(len(row_td) - 1):
                            tab_head_list.append(f'Характеристика {z - 2}') if z > 2 else None

                    get_rowspan = row_td[i].attrs.get('rowspan') if i == 1 else None
                    if rowspan > 1 and i == 1:
                        product_data.insert(i, '')
                        product_data.append(row_td[i].text.strip().replace('\n\t\t\t', ' ').replace(' ', ' '))

                        rowspan -= 1
                    else:
                        rowspan = int(get_rowspan) if get_rowspan and int(get_rowspan) > 1 else rowspan
                        product_data.append(row_td[i].text.strip().replace('\n\t\t\t', ' ').replace(' ', ' '))

                with open(f'{img_path}/{img_name}.jpg', 'wb') as file:
                    file.write(row_img)

                ready_data = list(zip(tab_head_list, product_data))
                json_dict = {'categories': category_list,
                             'self_category': self_category,
                             'img_name': f'{img_name}.jpg',
                             'manufacturer': manufield,
                             'tool': {name: char for name, char in ready_data}}

                with open(f'{folder_path}/{img_name}.json', 'w', encoding='utf-8') as file:
                    json.dump(json_dict, file, ensure_ascii=False, indent=4)

                ready_data_for_json.append(json_dict)
            print(ready_data_for_json)
