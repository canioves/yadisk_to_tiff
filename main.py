import requests
import os
import shutil
from PIL import Image
from zipfile import ZipFile
from urllib.parse import urlencode


class ImageMerger:
    def __init__(self, image_paths, row_size, margin):
        '''
        Класс для создания TIFF изображения из списка изображений.
        
        `image_paths`: список путей изображений
        `row_size`: количество изображений в одной строке
        `margin`: размер отступа от краев итогового изображения и расстояние между изображениями
        '''
        self.image_paths = image_paths
        self.row_size = row_size
        self.margin = margin
        self.image_list = self.__create_image_list()
        self.column_size = self.__get_column_size()
        self.canvas = self.__create_canvas()
        self.matrix = self.__create_matrix()

    def __create_image_list(self):
        return [Image.open(image) for image in self.image_paths]
    
    def __get_column_size(self):
        image_list_length = len(self.image_list)
        
        if self.row_size >= image_list_length:
            self.row_size = image_list_length
            column_size = 1
            return column_size
        
        if image_list_length % self.row_size == 0:
            column_size = image_list_length // self.row_size
        else:
            column_size = image_list_length // self.row_size + 1
        return column_size
        
    def __resize_images(self):
        min_height = min([image.height for image in self.image_list])
        min_width = min([image.width for image in self.image_list])
        resize_fn = lambda image: image.resize((int(image.width * min_height / image.height), int(image.height * min_width / image.width)), resample=Image.Resampling.BICUBIC)
        map(resize_fn, self.image_list)
        
    def __create_canvas(self):
        max_width = max([image.width for image in self.image_list])
        max_height = max([image.height for image in self.image_list])
        canvas_width = (max_width + self.margin) * self.row_size + self.margin
        canvas_height = (max_height + self.margin) * self.column_size + self.margin
        canvas = Image.new('RGB', (canvas_width, canvas_height), color=(255, 255, 255))
        return canvas
    
    def __create_matrix(self):
        matrix = []
        for i in range(self.column_size):
            column_list = [None] * self.row_size
            for j in range(self.row_size):
                idx = i * self.row_size + j
                if idx == len(self.image_list):
                    break
                column_list[j] = self.image_list[idx]
            matrix.append(column_list)
        return matrix
    
    def merge(self):
        pos_y = self.margin
        for i in range(len(self.matrix)):
            pos_x = self.margin
            for j in range(len(self.matrix[i])):
                if self.matrix[i][j] != None:
                    self.canvas.paste(self.matrix[i][j], (pos_x, pos_y))
                    pos_x += self.matrix[i][j].width + self.margin
            pos_y += self.matrix[i][0].height + self.margin
    
    def save_merged(self, number):
        self.canvas.save(f'output/Result {number}.tiff', 'TIFF')
    


def get_download_link(public_url):
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    result_url = base_url + urlencode(dict(public_key=public_url))
    response = requests.get(result_url)
    return response.json()['href']

def get_zip(url, filename, path=""):
    with open(os.path.join(path, filename), 'wb') as file:
        download_repsonse = requests.get(url)
        file.write(download_repsonse.content)
    
    
if __name__ == '__main__':
        
    download_link = get_download_link('https://disk.yandex.ru/d/V47MEP5hZ3U1kg')
    get_zip(download_link, 'data.zip')

    with ZipFile('data.zip', 'r') as zip:
        zip.extractall('unpacked')

    try:
        os.mkdir('output')
        file_number = 1
    except:
        files_list = os.listdir('output')
        last_file = files_list[len(files_list) - 1]
        file_number = int(last_file.split(' ')[1].split('.')[0]) + 1

    for root, dirs, files in os.walk('unpacked'):
        if len(dirs) == 0:
            files_paths = [os.path.join(root, file) for file in files]
            image_merger = ImageMerger(files_paths, 3, 50)
            image_merger.merge()
            image_merger.save_merged(file_number)
            file_number += 1
            
    shutil.rmtree('unpacked')
    os.remove('data.zip')
    