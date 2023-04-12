import os
import json
import shutil
import requests

from vk_user import VkUser
from ya_loader import YaUploader
from progress.bar import Bar


class Photo_size:

    def __init__(self, width, height, photo_type, url):
        self.W = width
        self.H = height
        self.type = photo_type
        self.url = url

    def __lt__(self, other):
        if not isinstance(other, Photo_size):
            return
        size1 = self.W * self.H
        size2 = other.W * other.H
        if size1 > 0 and size2 > 0:
            return size1 < size2
        sequence = 'smxyzw'
        return sequence.find(self.type) < sequence.find(other.type)


def main():
    directory = os.path.join(os.getcwd(), 'photos')
    try:
        os.mkdir(directory)
    except OSError:
        shutil.rmtree(directory)
        os.mkdir(directory)

    user_id = input('Введите ID пользователя VK: ')
    if user_id.strip() == '':
        user_id = None
    token_vk = input('Введите токен для VK: ')
    try:
        count = int(input('Введите количество фотографий: '))
    except ValueError:
        count = 5
    album_id = input('Введите идентификатор альбома '
                     '(wall, profile или saved): ')
    if album_id.strip() == '':
        album_id = 'profile'
    token_yadisk = input('Введите токен для ЯндексДиска: ')

    vk_client = VkUser(token_vk, '5.131')
    data = vk_client.get_photos(user_id=user_id, count=count, album=album_id)
    if data is None:
        shutil.rmtree(directory)
        return

    result_data = []
    bar = Bar('Получение фотографий из VK: ', max=len(data))
    for photo in data:
        bar.next()
        file_name = str(photo['likes']['count']) + '.jpg'
        photo_sizes = []
        for size in photo['sizes']:
            photo_sizes.append(Photo_size(size['width'], size['height'],
                                          size['type'], size['url']))
        photo_sizes.sort(reverse=True)
        response = requests.get(photo_sizes[0].url)
        try:
            with open('photos/' + file_name, 'xb') as file:
                file.write(response.content)
        except FileExistsError:
            file_name = file_name[:-4] + '_' + str(photo['date']) + '.jpg'
            with open('photos/' + file_name, 'wb') as file:
                file.write(response.content)

        result_data.append({'file_name': file_name,
                            'size': photo_sizes[0].type})
    bar.finish()

    with open('result.json', 'w') as file:
        json.dump(result_data, file, ensure_ascii=False, indent=2)

    path_to_file = '/backup_photo/'
    uploader = YaUploader(token_yadisk)
    uploader.upload(path_to_file, 'photos')

    shutil.rmtree(directory)


if __name__ == '__main__':
    main()
