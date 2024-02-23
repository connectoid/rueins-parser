import os
import shutil

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from PIL import Image
import pymorphy2

from database.orm import create_download

base_url = 'https://rueins.ru/'

ua = UserAgent()

downloads_dir = '/var/www/www-root/data/www/manualbase.ru/uploads/download/electro'
downloads_thumbs_dir = '/var/www/www-root/data/www/manualbase.ru/uploads/download/electro/thumbs'

# downloads_dir = 'pdf'
# downloads_thumbs_dir = 'pdf/thumbs'




headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


def get_fake_headers():
    fake_headers = {'user-agent': ua.random.strip()}
    return fake_headers


def get_categories_list(url):
    categories_list = []
    response = requests.post(url=url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    links = soup.find_all('a', class_='section-link')
    categories_links = [link['href'] for link in links]
    names = soup.find_all('span', class_='section-name')
    cat_names = [name.text for name in names]
    categories_list = list(zip(cat_names, categories_links))
    return categories_list


def get_brands_list(url): 
    brands_list = []
    response = requests.post(url=url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    div = soup.find_all('div', class_='tabs__content')[1]
    divs = div.find_all('div', class_='letter_items')
    for div in divs:
        brand_list = []
        brand = div.find('a')
        brand_url = brand['href']
        brand_title = brand.text
        brand_list.append(brand_title)
        brand_list.append(brand_url)
        brands_list.append(brand_list)
    return brands_list

def change_case(name, case):
    morph = pymorphy2.MorphAnalyzer()
    tmp_word = morph.parse(name)[0]
    cased = tmp_word.inflect({case})
    new_name = cased.word
    return new_name

def get_models_list(url):
    model_urls = []
    model_titles = []
    response = requests.post(url=url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    nav_links = soup.find('div', class_='nav-links')
    if nav_links:
        pages = nav_links.find_all('a', class_='page-numbers')
        pages = [page.text for page in pages]
        pages_count = int(pages[-2])
        for page in range(2, pages_count + 1):
                new_url = f'{url}page/{page}/'
                response = requests.post(url=new_url, headers=headers)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'lxml')
                divs = soup.find_all('div', class_='entry-title')
                spans = soup.find_all('span', {'itemprop': 'headline'})
                for span in spans:
                    model_name = span.text.replace('Инструкция к ', '')
                    model_name = change_case(model_name, 'nomn')
                    model_titles.append(model_name)
                for div in divs:
                    model_urls.append(div.find('a')['href'])
    else:
        divs = soup.find_all('div', class_='entry-title')
        spans = soup.find_all('span', {'itemprop': 'headline'})
        for span in spans:
            model_name = span.text.replace('Инструкция к ', '')
            model_name = change_case(model_name, 'nomn')
            model_titles.append(model_name)
        for div in divs:
            model_urls.append(div.find('a')['href'])
    models_list = list(zip(model_titles, model_urls))
    return models_list


def get_manual_link(url):
    response = requests.post(url=url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    manual_link = []
    try:
        file_link = soup.find('div', class_='main-content-iframe').find('a')['href']
        thumb_link = soup.find('div', class_='main-content-iframe').find('img')['src']
        file_name = file_link.split('/')[-1]
        thumb_name = thumb_link.split('/')[-1]
        manual_link.append(file_name)
        manual_link.append(file_link)
        manual_link.append(thumb_name)
        manual_link.append(thumb_link)
    except TypeError as e:
        print(f'Ошибка парсинга: {e}')
        return False
    except AttributeError as e:
        print(f'Ошибка парсинга: {e}')
        return False
    return manual_link


def download_file_from_url(url, file_name, dest_folder, is_thumb=False):
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        file_path = f"{dest_folder}/{file_name}"
        with open(file_path, mode="wb") as file:
            file.write(response.content)
        filesize = os.path.getsize(file_path)
        if is_thumb:
            dst = f"{dest_folder}/mini/{file_name}"
            shutil.copyfile(file_path, dst)
            image = Image.open(dst)
            image.thumbnail((200, 200))
            image.save(dst)
        return filesize
    else:
        print(f'Ошибка сохранения файла {file_name}: {response.status_code}')
        return None


def create_xfields(cat_name='', brand_name='', lang='русском', format='pdf'):
    example = 'type|коммуникатор||develop|ACER||lang|русском||fformat|pdf||board|'
    xfields = f'type|{cat_name}||develop|{brand_name}||lang|{lang}||fformat|{format}||board|'
    return xfields


all_brands = get_brands_list(base_url)
brands = []
brands.append(all_brands[1])
for brand in brands:
    categories = get_categories_list(brand[1])
    for category in categories:
        models = get_models_list(category[1])
        for model in models:
            manual_link = get_manual_link(model[1])
            file_name = manual_link[0].replace(' ', '-')
            file_link = manual_link[1]
            thumb_name = manual_link[2]
            thumb_link = manual_link[3]
            filesize = download_file_from_url(file_link, file_name, downloads_dir)
            thumbsize = download_file_from_url(thumb_link, thumb_name, downloads_thumbs_dir, is_thumb=True)
            if filesize:
                print(f'Файл {manual_link[0]} сохранен, размер: {filesize}')
                xfields = create_xfields(category[0], brand[0])
                # print(f'{manual_link[0]}, {manual_link[1]}, {manual_link[2]}, {xfields}, {filesize}')
                if create_download(model[0], xfields, 6, file_name, filesize, thumb_name):
                    print('Запись успешно добавлена в БД')
            else:
                print('Download error')