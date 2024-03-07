import requests
import os

from bs4 import BeautifulSoup
from pdf2image import convert_from_path
from PIL import Image
import pypdfium2 as pdfium


from database.orm import create_download, get_manual_titles_from_donor


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
base_download_url = 'https://mnogo-dok.ru/download.php'
base_url = 'https://mnogo-dok.ru'




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
    try:
        cat_urls = soup.find('div', class_='tech-items flex').find_all('a')
        cat_names = soup.find('div', class_='tech-items flex').find_all('span')
        cat_urls = [base_url + cat['href'] for cat in cat_urls]
        cat_names = [name.text for name in cat_names]
        all_cats = list(zip(cat_names, cat_urls))
        return all_cats
    except Exception as e:
        print(f'Ошибка получения категории: {e}')
        return False

def download_file_by_id(downloads_dir, file_id, file_name='checkout.pdf'):
    download_url = f'{base_download_url}?id={file_id}'
    response = requests.get(url=download_url, headers=headers)
    if response.status_code == 200:
        filename_string = response.headers['Content-Disposition']
        try:
            ext = filename_string.split('filename="')[-1].strip('"').split('.')[-1]
        except Exception as e:
            print(f'Ошибка получения разрешения, оставляем PDF: {e}')
            ext = 'pdf'
        file_name = f'{file_name}.{ext}'.replace(' ', '-').lower()
        file_path = f'{downloads_dir}/{file_name}'
        with open(file_path, mode="wb") as file:
            file.write(response.content)
        filesize = os.path.getsize(file_path)
        if filesize > MAX_FILE_SIZE:
            print(f'~~~~   ~~~~   ~~~~   Размер ({filesize} kb) файла больше максимального ({MAX_FILE_SIZE}), Удаляем!')
            os.remove(file_path)
            return False, False
        return file_name, filesize
    else:
        print(f'Ошибка сохранения файла {file_name}: {response.status_code}')
        return False, False

def download_thumbnail(downloads_dir, downloads_thumbs_dir, file_name):
    try:
        file_name_wo_pdf = file_name.replace('.pdf', '')
    except Exception as e:
        print(f'Файл {file_name} не PDF')
        file_name_wo_pdf = file_name
    file_path = f'{downloads_dir}/{file_name}'
    downloads_thumbs_dir_mini = f'{downloads_thumbs_dir}/mini'
    thumbnail_file_name = f'{downloads_thumbs_dir}/{file_name_wo_pdf}.jpg'
    thumbnail_file_name_mini = f'{downloads_thumbs_dir_mini}/{file_name_wo_pdf}.jpg'
    try:
        pdf = pdfium.PdfDocument(file_path)
        page = pdf[0]
        image = page.render(scale=4).to_pil()
        image.save(thumbnail_file_name)
        image.save(thumbnail_file_name_mini)

        mini_image = Image.open(thumbnail_file_name_mini)
        mini_image.thumbnail((200, 200))
        mini_image.save(thumbnail_file_name_mini)
        return f'{file_name_wo_pdf}.jpg'
    except Exception as e:
        print(f'Ошибка сохранения миниатюры: {e}')
        return False

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


letters = [
    # ['a', 4411], #2878
    # ['b', 4412], #5580
    # ['c', 4413], #2209
    # ['d', 4414], #2944
    # ['e', 4415], #2679
    # ['f', 4416], #776
    # ['g', 4417], #2118
    # ['h', 4418], #4065
    # ['i', 4425], #1258
    # ['j', 4419], #1461
    # ['k', 4420], #1325    #28247
    ['l', 4421],
    ['m', 4422],
    ['n', 4423],
    # ['o', 4424],
    # ['p', 4425],
    # ['q', 4426],
    # ['r', 4427],
    # ['s', 4428],
    # ['t', 4429],
]

MAX_FILE_SIZE = 15000000
MAX_ITERATIONS = 3

def main(downloads_dir, downloads_thumbs_dir, manual_titles):
    count = 1
    all_brands = get_brands(base_url)

    for brand in all_brands:
        if brand[0][:1].upper() == FIRST_LETTER.upper():
            all_cats = get_categories(brand[1])
            if all_cats:
                for cat in all_cats:
                    all_models = get_models(cat[1])
                    for model in all_models:
                        model_name = model[0].strip()
                        model_name = model_name.replace('/', '-')
                        model_name = model_name.replace('\\', '-')
                        model_name = model_name.replace('+', '-')
                        if model_name.upper() not in manual_titles:
                            brand_name = brand[0]
                            category_name = cat[0]
                            file_name = f'{model_name}-00{count}'.strip()
                            model_id = model[1]
                            xfields = create_xfields(category_name, brand_name)
                            full_file_name, file_size = download_file_by_id(downloads_dir, model_id, file_name)
                            thumbnale_file =  download_thumbnail(downloads_dir, downloads_thumbs_dir, full_file_name)
                            if full_file_name:
                                create_download(model_name, xfields, CAT_ID, full_file_name, file_size, thumbnale_file)
                                print(f'{count}. {model_name}: {model_id}')
                                count += 1
                            else:
                                pass
                            # if count > MAX_ITERATIONS:
                            #     return
                        else:
                            print(f'=========> Модель {model_name} уже есть в базе. Пропускаем')
            else:
                print('Пропускаем категорию')


if __name__ == '__main__':
    manual_titles = get_manual_titles_from_donor()
    manual_titles = [title.upper() for title in manual_titles]

    for brand_letter in letters:
        FIRST_LETTER = brand_letter[0]
        CAT_ID = brand_letter[1]
        downloads_dir = f'/var/www/www-root/data/www/manualbase.ru/uploads/download/{FIRST_LETTER}'
        downloads_thumbs_dir = f'/var/www/www-root/data/www/manualbase.ru/uploads/download/{FIRST_LETTER}/thumbs'
        if not os.path.exists(f'{downloads_dir}/thumbs'):
            os.makedirs(f'{downloads_dir}/thumbs')
        if not os.path.exists(f'{downloads_dir}/thumbs/mini'):
            os.makedirs(f'{downloads_dir}/thumbs/mini')
        main(downloads_dir, downloads_thumbs_dir, manual_titles)