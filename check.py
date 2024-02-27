import requests
import os

from bs4 import BeautifulSoup


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
base_download_url = 'https://mnogo-dok.ru/download.php'
base_url = 'https://mnogo-dok.ru'

pioneers = 'https://mnogo-dok.ru/instrukcii/sendvalues/type/%D0%90%D0%B2%D1%82%D0%BE%D1%82%D0%B5%D1%85%D0%BD%D0%B8%D0%BA%D0%B0/%D0%90%D0%B2%D1%82%D0%BE%D0%BC%D0%B0%D0%B3%D0%BD%D0%B8%D1%82%D0%BE%D0%BB%D1%8B/Pioneer/'


def get_brands(url):
    all_brands = []
    response = requests.post(url=url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    blocks = soup.find_all('ul', class_='catalog')
    brands = blocks[1].find_all('a')
    all_brands = [[brand.text, base_url + brand['href']] for brand in brands if brand['href'] != '#']
    return all_brands


def get_models(url):
    all_models = []
    response = requests.post(url=url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    blocks = soup.find_all('div', class_='ins-block brand-block')
    for block in blocks:
        models = block.find_all('a')
        models = [[model.text, model['href'].split('sendvalues')[1].split('/')[1]] for model in models if model['href'] != '#']
        for model in models:
            all_models.append(model)
    return all_models


def get_categories(url):
    all_cats = []
    response = requests.post(url=url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    cat_urls = soup.find('div', class_='tech-items flex').find_all('a')
    cat_names = soup.find('div', class_='tech-items flex').find_all('span')
    cat_urls = [base_url + cat['href'] for cat in cat_urls]
    cat_names = [name.text for name in cat_names]
    all_cats = list(zip(cat_names, cat_urls))
    return all_cats


def download_file_by_id(file_id, file_name='checkout.pdf'):
    response = requests.get(url=f'{base_url}?id={file_id}', headers=headers)
    if response.status_code == 200:
        file_path = f"{file_name}"
        with open(file_path, mode="wb") as file:
            file.write(response.content)
        filesize = os.path.getsize(file_path)
        return filesize
    else:
        print(f'Ошибка сохранения файла {file_name}: {response.status_code}')
        return None


# filesize = download_file_by_id('100895')
# print(filesize)
    
# all_models = get_models(pioneers)
count = 1
all_brands = get_brands(base_url)

for brand in all_brands:
    print('='*25, brand[0])
    all_cats = get_categories(brand[1])
    for cat in all_cats:
        print('='*25, cat[0])
        all_models = get_models(cat[1])
        for model in all_models:
            print(f'{count}. {model[0]}: {model[1]}')
            count += 1