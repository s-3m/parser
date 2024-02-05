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
            tab_head_list = [head.text.strip() for head in tab_heads if head.text]
            product_rows = tab_heads[0].parent.find_next_siblings('tr')
            product_rows_list = [i for i in product_rows if len(i) > 10]
            for row in product_rows_list:
                row_td = row.find_all('td')
                product_data = []
                for i in range(len(row_td)-1):
                    get_rowspan = row_td[i].attrs.get('rowspan')
                    if rowspan > 1 and i == 1:
                        product_data.insert(i, '')
                        product_data.append(row_td[i].text.strip())
                        rowspan -= 1
                    else:
                        rowspan = int(get_rowspan) if get_rowspan and int(get_rowspan) > 1 else rowspan
                        product_data.append(row_td[i].text.strip())
                ready_data = list(zip(tab_head_list, product_data))
                print(ready_data)

