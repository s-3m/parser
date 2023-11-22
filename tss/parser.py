import json
import os

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pprint import pprint

agent = UserAgent()

link = 'https://www.tss-russia.com/catalog/blok-konteynery/'
domen = 'https://www.tss-russia.com'


def get_data():
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                         '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
               'User-Agent': agent.random}

    # ------------------------------ Получение списка ссылок ----------------------------

    resp = requests.get(url=link, headers=headers).text

    bs = BeautifulSoup(resp, 'lxml')

    # res = bs.findAll(class_='name')
    res = bs.find(class_='seometa-tags-wrapper').findAll('a')

    # Получение списка ссылок на категории товаров
    category_links_list = [domen + i['href'] for i in res]

    # category_links_list = ["https://www.tss-russia.com/catalog/svarochnye-elektrostantsii/"]

    # Получение списка ссылок на карточки товаров с учётом пагинации
    item_links_list = []
    for category_link in category_links_list:
        resp = requests.get(category_link, headers=headers).text
        bs = BeautifulSoup(resp, 'lxml')
        pagination = bs.find(class_='catalog-pagination')
        max_pagination = 1
        if pagination:
            pagination = pagination.findAll('a')
            max_pagination = int(pagination[-2].text)

        for i in range(1, max_pagination + 1):
            resp = requests.get(f"{category_link}?PAGEN_1={i}", headers=headers).text
            bs = BeautifulSoup(resp, 'lxml')
            bs_list = bs.findAll(class_="column large-6 xxlarge-8 column-info")
            item_links = [domen + i.find('a').get("href") for i in bs_list]
            item_links_list.extend(item_links)
    item_links_list = set(item_links_list)
    pprint(len(item_links_list))
    exit()

    pprint(item_links_list)
    print('\n')

    for num, item_link in enumerate(item_links_list):
        print(f'\rДелаю {num + 1} из {len(item_links_list)}', end='')
        resp = requests.get(item_link, headers=headers)
        bs = BeautifulSoup(resp.text, 'lxml')
        category = bs.find(class_='breadcrumbs').findAll('span')[1].text

        item_title = bs.find('h1', itemprop='name').text
        item_title = item_title.replace('/', '_')

        # ------------------------------ Получение и запись изображений ----------------------------

        if not os.path.exists(category):
            os.mkdir(category)

        if not os.path.exists(f'{category}/{item_title}'):
            os.mkdir(f'{category}/{item_title}')

        img_folder = f'{category}/{item_title}/img'
        if not os.path.exists(img_folder):
            os.mkdir(img_folder)

        images_tag = bs.find('div', class_='product-preview relative').findAll('a', class_="item")
        images_list_links = [domen + i.get('href') for i in images_tag]

        for i in images_list_links:
            img_name = i.split('/')[-1]
            resp = requests.get(i).content
            with open(f'{img_folder}/{img_name}', 'wb') as file:
                file.write(resp)

        # ------------------------------ Получение ТХ ----------------------------

        tech_data = bs.find(id='product-tab-1').findAll('td')

        tech_dict = {}
        main_key = ''
        sub_key = ''

        for i in tech_data:
            if i.get('colspan'):
                main_key = i.text
                tech_dict[main_key] = {}
            elif i.get('class')[0] == 'cell_name':
                sub_key = i.text
                tech_dict[main_key][sub_key] = ''
            elif i.get('class')[0] == 'cell_value':
                tech_dict[main_key][sub_key] = i.text

        try:
            del tech_dict['']
        except KeyError:
            pass
        # ------------------------------ Получение описания, наименования и категорий ----------------------------
        try:
            descr_data = bs.find(id='product-tab-2').find(class_='product-accordion-tabs-wrap').text
            pure_descr_data = descr_data.replace('\n\n\n', '\n').replace('\n\n', '\n').replace('\n ', '\n').strip()
            item_name = ' '.join(item_title.split(' ')[:-1]).replace('_', '/')
            print('\n' f'ВИДЕО ОБЗОР {item_name.upper()}')
            if f'ВИДЕО ОБЗОР {item_name.upper()}' in pure_descr_data:
                pure_descr_data = pure_descr_data.replace(f'ВИДЕО ОБЗОР {item_name.upper()}', '')

            tech_dict['description'] = pure_descr_data.replace('\n\n\n', '\n')
        except AttributeError:
            pass

        tech_dict['title'] = item_title
        tech_dict['main_category'] = bs.findAll('li', itemprop='itemListElement')[1].find('a').text.strip()
        tech_dict['sub_category'] = bs.findAll('li', itemprop='itemListElement')[2].find('a').text.strip()

        with open(f'{category}/{item_title}/data.json', 'w', encoding='utf-8') as file:
            json.dump(tech_dict, file, indent=4, ensure_ascii=False)


def main():
    get_data()


if __name__ == '__main__':
    main()
