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
            rowspan = 0
            colspan = 0
            tab_heads = table.find_all('td', style=lambda x: x and 'background-color: #dcdcdc;' in x)
            # tab_head_list = [head.text.strip() for head in tab_heads if head.text][:-4]
            product_rows = tab_heads[0].find_parent('tr').find_next_siblings('tr')
            product_rows_list = [i for i in product_rows if len(i) > 5]
            for row in product_rows_list:
                tab_head_list = [head.text.strip() for head in tab_heads if head.text.strip() != '' and head.text.strip()[0].isalpha()]
                row_td = row.find_all('td')
                product_data = []
                # if len(row_td[3:]) < len(tab_head_list) - 3:
                #     tab_head_list = ['Артикул', 'Фото', 'Модель']
                #     for i in range(len(row_td) - 1):
                #         tab_head_list.append(f'Характеристика {i-2}') if i > 2 else None
                #         product_data.append(row_td[i].text)
                # else:
                for i in range(len(row_td) - 1):
                    #-------
                    if len(row_td[3:]) < len(tab_head_list) - 3:
                        tab_head_list = ['Артикул', 'Фото', 'Модель']
                        for z in range(len(row_td) - 1):
                            tab_head_list.append(f'Характеристика {z - 2}') if z > 2 else None
                    #------
                    get_rowspan = row_td[i].attrs.get('rowspan') if i == 1 else None
                    if rowspan > 1 and i == 1:
                        product_data.insert(i, '')
                        product_data.append(row_td[i].text.strip())
                        rowspan -= 1
                    else:
                        rowspan = int(get_rowspan) if get_rowspan and int(get_rowspan) > 1 else rowspan
                        product_data.append(row_td[i].text.strip())
                ready_data = list(zip(tab_head_list, product_data))
                print(ready_data)
