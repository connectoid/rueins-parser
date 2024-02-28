import requests
import os

from bs4 import BeautifulSoup

div_class = 'letter_items'
url = 'https://rueins.ru/'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

response = requests.post(url=url, headers=headers)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'lxml')
divs = soup.find_all('div', class_='tabs__content')
brands = divs[1].find_all('a')
brands = [brand.text for brand in brands]

brands_list = []
count = 1
for brand in brands:
    brands_list.append(f'{count}. {brand}\n')
    count += 1

with open('brands_list.txt', mode="w") as file:
            file.writelines(brands_list)