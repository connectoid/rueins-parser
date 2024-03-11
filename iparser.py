import requests
import os
import os.path

from bs4 import BeautifulSoup
from pdf2image import convert_from_path
from PIL import Image
import pypdfium2 as pdfium

proxies = {
#    'http': 'socks5://ZGTxtv:gnttyS@194.67.214.57:9658',
#    'https': 'socks5://ZGTxtv:gnttyS@194.67.214.57:9658',
   'http': 'socks5://wGJX8p:unz2MG@88.218.72.74:9060',
   'https': 'socks5://wGJX8p:unz2MG@88.218.72.74:9060',
}

# from database.orm import create_download, get_manual_titles_from_donor


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
base_download_url = 'https://mcgrp.ru/api/files/get2'
base_url = 'https://mcgrp.ru'

data = {'fileid': "1705", '_token': "yhZ4RBrHXKiUVv97EDTQYfVb3jntnoyb5V0qBH2j"}

test_url = 'https://mcgrp.ru/api/files/get2?fileid=1641&_token=yhZ4RBrHXKiUVv97EDTQYfVb3jntnoyb5V0qBH2j'

ids = [
        '1557',
       ]


def get_manual(fileid, count):
    test_url = f'https://mcgrp.ru/api/files/get2?fileid={fileid}&_token=yhZ4RBrHXKiUVv97EDTQYfVb3jntnoyb5V0qBH2j'
    response = requests.post(url=test_url, headers=headers)
    if response.status_code == 200:
        # print(f'SUCCESS! RESPONSE STATUS CODE: {response.status_code}')
        json = response.json()
        json_result = json['result']
        if json_result == 'success':
            download_url = base_url + json['href']
            filename = json['filename']
            format = json['format']
            filename = f'{filename}.{format}'
            print(f'{count}. {download_url} - {filename}')
            # response = requests.get(url=download_url, proxies=proxies, headers=headers)

            # with open(filename, mode="wb") as file:
            #             file.write(response.content)

        elif json_result == 'error':
            json_message = json['message']
            print(f'{count}. JSON STATUS: {json_result}, MESSAGE: {json_message}')
        else:
              print(f'{count}.JSON STATUS: {json_result}')
    else:
        print(f'{count}. RESPONSE ERROR! RESPONSE STATUS CODE: {response.status_code}')

if __name__ == '__main__':
    for count, id in enumerate(range(1557, 1568)):
        get_manual(id, count)