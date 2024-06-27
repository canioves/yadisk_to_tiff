import requests
import os
import numpy as np
from PIL import Image, ImageDraw
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
        
def create_matrix(items_list, row_length, col_length):
    matrix = []
    for i in range(col_length):
        col_list = [None] * row_length
        for j in range(row_length):
            idx = i * row_length + j
            if idx == len(items_list):
                break
            col_list[j] = items_list[idx]
        matrix.append(col_list)
    return matrix

def create_canvas(image_list, row_length, col_length, margin):
    max_width = max([image.width for image in image_list])
    max_height = max([image.height for image in image_list])
    canvas_width = (max_width + margin) * row_length + margin
    canvas_height = (max_height + margin) * col_length + margin
    
    canvas = Image.new('RGB', (canvas_width, canvas_height), color=(255, 255, 255))
    return canvas

        
def merge_images(files_paths, row_length, margin):
    images = [Image.open(image) for image in files_paths]
    max_height = max([image.height for image in images])
    
    if row_length > len(images):
        row_length = len(images)
        col_length = 1
    else:
        col_length = len(images) // row_length + 1 if len(images) % row_length > 0 else len(images) // row_length
    
    matrix = create_matrix(images, row_length, col_length)
    canvas = create_canvas(images, row_length, col_length, margin)
    
    pos_y = margin
    for i in range(len(matrix)):
        pos_x = margin
        for j in range(len(matrix[i])):
            if matrix[i][j] != None:
                canvas.paste(matrix[i][j], (pos_x, pos_y))
                pos_x += matrix[i][j].width + margin
        pos_y += max_height + margin
        
    canvas.show()
    

download_link = get_download_link('https://disk.yandex.ru/d/V47MEP5hZ3U1kg')
get_zip(download_link, 'data.zip')

with ZipFile('data.zip', 'r') as zip:
    zip.extractall('unpacked')
    
for root, dirs, files in os.walk('unpacked'):
    if len(dirs) == 0:
        files_paths = [os.path.join(root, file) for file in files]
        print(root)
        merge_images(files_paths, 2, 50)