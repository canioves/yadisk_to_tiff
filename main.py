import requests
import os
from zipfile import ZipFile
from urllib.parse import urlencode

def get_download_link(public_url):
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    result_url = base_url + urlencode(dict(public_key=public_url))
    response = requests.get(result_url)
    return response.json()['href']

def get_zip(url, filename, path=""):
    with open(os.path.join(path, filename), 'wb') as file:
        download_repsonse = requests.get(url)
        file.write(download_repsonse.content)

download_link = get_download_link('https://disk.yandex.ru/d/V47MEP5hZ3U1kg')
get_zip(download_link, 'data.zip')

with ZipFile('data.zip', 'r') as zip:
    zip.extractall('unpacked')