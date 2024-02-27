import os
import shutil
from time import time

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from PIL import Image
import pymorphy2
from pypdf import PdfReader, PdfWriter
import aspose.pdf as ap


from database.orm import create_download, get_manual_titles_from_donor

base_url = 'https://rueins.ru/'

bosch_url = 'https://rueins.ru/?s=+Bosch+%28%D0%91%D0%BE%D1%88%29+Serie%7C2+FEL053MS2'

ua = UserAgent()

downloads_dir = '/var/www/www-root/data/www/manualbase.ru/uploads/download/electro'
downloads_thumbs_dir = '/var/www/www-root/data/www/manualbase.ru/uploads/download/electro/thumbs'

# downloads_dir = 'pdf'
# downloads_thumbs_dir = 'pdf/thumbs'

MAX_FILE_SIZE = 100000000


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
    cat_names = [change_case(name.text, 'nomn').replace('Инструкция по эксплуатация ', '') for name in names]
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


def change_case(sentense, case):
    words_list = sentense.split()
    new_words_list = []
    for word in words_list:
        if isinstance(word, str):
            try:
                morph = pymorphy2.MorphAnalyzer()
                tmp_word = morph.parse(word)[0]
                new_word = tmp_word.inflect({case})
                new_words_list.append(new_word.word)
            except Exception as e:
                new_words_list.append(word)
        else:
            new_words_list.append(word)
    new_sentense = ' '.join(new_words_list)
    return new_sentense.capitalize()


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
        if filesize > MAX_FILE_SIZE:
            print(f'File size more than MAX_FILE_SIZE ({MAX_FILE_SIZE}). Skip')
            os.remove(file_path)
            return None
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


def compress_pdf(file_name):
    reader = PdfReader(file_name)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    for page in writer.pages:
        for img in page.images:
            img.replace(img.image, quality=50)
    with open(file_name, "wb") as f:
        writer.write(f)


def main():
    print('Start requesting models list in database')
    manual_titles = get_manual_titles_from_donor()
    manual_titles = [title.upper() for title in manual_titles]
    print('Stop requesting models list in database')
    all_brands = get_brands_list(base_url)
    all_brands = all_brands[49:]
    print(f'All brands count: {len(all_brands)}')
    count = 1
    for brand in all_brands:
        categories = get_categories_list(brand[1])
        for category in categories:
            models = get_models_list(category[1])
            for model in models:
                manual_link = get_manual_link(model[1])
                if manual_link:
                    file_name = manual_link[0].replace(' ', '-')
                    model_name = manual_link[0].split('.')[0]
                    full_model_name = f'{brand[0]} {model_name}'
                    file_link = manual_link[1]
                    thumb_name = manual_link[2]
                    thumb_link = manual_link[3]
                    if full_model_name.upper() not in manual_titles:
                        filesize = download_file_from_url(file_link, file_name, downloads_dir)
                        thumbsize = download_file_from_url(thumb_link, thumb_name, downloads_thumbs_dir, is_thumb=True)
                        if filesize:
                            # print(f'Файл {manual_link[0]} сохранен, размер: {filesize}')
                            xfields = create_xfields(category[0].replace(brand[0], '').capitalize(), brand[0])
                            # print(f'{manual_link[0]}, {manual_link[1]}, {manual_link[2]}, {xfields}, {filesize}')
                            if create_download(full_model_name, xfields, 6, file_name, filesize, thumb_name):
                                print(f'{count}. Модель {full_model_name} успешно добавлена в БД')
                                count += 1
                                if count >= 600:
                                    return None
                        else:
                            print('Download error or file is too big')
                    else:
                        print(f'Model {full_model_name} already exists. Passing')
                else:
                    print(f'Ссылка на инструкцию для модели {model[0]} не получена.')


if __name__ == '__main__':
    main()