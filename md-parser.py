import requests
import os

from bs4 import BeautifulSoup

from database.orm import create_download, get_manual_titles_from_donor

downloads_dir = '/var/www/www-root/data/www/manualbase.ru/uploads/download/electro'
downloads_thumbs_dir = '/var/www/www-root/data/www/manualbase.ru/uploads/download/electro/thumbs'


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
base_download_url = 'https://mnogo-dok.ru/download.php'
base_url = 'https://mnogo-dok.ru'

pioneers = 'https://mnogo-dok.ru/instrukcii/sendvalues/type/%D0%90%D0%B2%D1%82%D0%BE%D1%82%D0%B5%D1%85%D0%BD%D0%B8%D0%BA%D0%B0/%D0%90%D0%B2%D1%82%D0%BE%D0%BC%D0%B0%D0%B3%D0%BD%D0%B8%D1%82%D0%BE%D0%BB%D1%8B/Pioneer/'

MAX_FILE_SIZE = 10000000


def get_brands(url):
    all_brands = []
    response = requests.post(url=url, headers=headers)
    response.encoding = 'windows-1251'
    soup = BeautifulSoup(response.text, 'lxml')
    blocks = soup.find_all('ul', class_='catalog')
    brands = blocks[1].find_all('a')
    all_brands = [[brand.text, base_url + brand['href']] for brand in brands if brand['href'] != '#']
    return all_brands


def get_models(url):
    all_models = []
    response = requests.post(url=url, headers=headers)
    response.encoding = 'windows-1251'
    soup = BeautifulSoup(response.text, 'lxml')
    blocks = soup.find_all('div', class_='ins-block brand-block')
    for block in blocks:
        models = block.find_all('a')
        models = [[model.text, model['href'].split('sendvalues')[1].split('/')[1], base_url + model['href']]  for model in models if model['href'] != '#']
        for model in models:
            all_models.append(model)
    return all_models


def get_categories(url):
    all_cats = []
    response = requests.post(url=url, headers=headers)
    response.encoding = 'windows-1251'
    soup = BeautifulSoup(response.text, 'lxml')

    ########## TRY EXCEPT !
    
    cat_urls = soup.find('div', class_='tech-items flex').find_all('a')
    cat_names = soup.find('div', class_='tech-items flex').find_all('span')
    cat_urls = [base_url + cat['href'] for cat in cat_urls]
    cat_names = [name.text for name in cat_names]
    all_cats = list(zip(cat_names, cat_urls))
    return all_cats


def download_file_by_id(downloads_dir, file_id, file_name='checkout.pdf'):
    download_url = f'{base_download_url}?id={file_id}'
    print(download_url)
    response = requests.get(url=download_url, headers=headers)
    print(response.status_code)
    if response.status_code == 200:
        file_name = f'{file_name}.pdf'
        file_path = f'{downloads_dir}/{file_name}'
        with open(file_path, mode="wb") as file:
            file.write(response.content)
        filesize = os.path.getsize(file_path)
        return file_name, filesize
    else:
        print(f'Ошибка сохранения файла {file_name}: {response.status_code}')
        return False, False


def create_xfields(cat_name='', brand_name='', lang='русском', format='pdf'):
    example = 'type|коммуникатор||develop|ACER||lang|русском||fformat|pdf||board|'
    xfields = f'type|{cat_name}||develop|{brand_name}||lang|{lang}||fformat|{format}||board|'
    return xfields


def get_file_size(url):
    response = requests.post(url=url, headers=headers)
    response.encoding = 'windows-1251'
    soup = BeautifulSoup(response.text, 'lxml')
    file_size = soup.find('span', class_='file_size').text
    return file_size

# filesize = download_file_by_id('100895')
# print(filesize)
    
# all_models = get_models(pioneers)

FIRST_LETTER = 'a'
CAT_ID = '4411'
downloads_dir = f'/var/www/www-root/data/www/manualbase.ru/uploads/download/{FIRST_LETTER}'
downloads_thumbs_dir = f'/var/www/www-root/data/www/manualbase.ru/uploads/download/{FIRST_LETTER}/thumbs'


def main():
    count = 1
    all_brands = get_brands(base_url)

    for brand in all_brands:
        if brand[0][:1].upper() == FIRST_LETTER.upper():
            all_cats = get_categories(brand[1])
            for cat in all_cats:
                all_models = get_models(cat[1])
                for model in all_models:
                    brand_name = brand[0]
                    category_name = cat[0]
                    model_name = f'{brand[0]}-{model[0]}-00{count}'
                    model_id = model[1]
                    print(f'{count}. {model_name}: {model_id}')
                    xfields = create_xfields(category_name, brand_name)
                    file_name, file_size = download_file_by_id(downloads_dir, model_id, model_name)
                    if file_name:
                        create_download(model_name, xfields, CAT_ID, file_name, file_size, 'thumble_path')
                    count += 1
                    return

if __name__ == '__main__':
    main()