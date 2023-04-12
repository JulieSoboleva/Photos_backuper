import os
import requests

from progress.bar import Bar


class YaUploader:

    def __init__(self, token: str):
        self.token = token

    def _get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def _create_folder(self, disk_file_path):
        create_folder_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self._get_headers()
        params = {'path': disk_file_path }
        response = requests.put(create_folder_url, headers=headers,
                                params=params)
        return response.status_code

    def _get_upload_link(self, disk_file_path):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self._get_headers()
        params = {'path': disk_file_path, 'overwrite': 'true'}
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json()

    def upload(self, disk_file_path, dir_name):
        status_code = self._create_folder(disk_file_path)
        if status_code not in (201, 409):
            return

        work_dir = os.path.join(os.getcwd(), dir_name)
        files = os.listdir(work_dir)
        bar = Bar('Сохранение фотографий на ЯндексДиск: ', max=len(files))
        counter = 0
        for file in files:
            bar.next()
            full_name = os.path.join(work_dir, file)
            if os.path.isfile(full_name):
                href = (self._get_upload_link(disk_file_path + file)
                        .get('href', ''))
                with open(full_name, 'rb') as f:
                    response = requests.put(href, data=f)
                response.raise_for_status()
                if response.status_code == 201:
                    counter += 1

        if counter != len(files):
            print(f'Сохранено {counter} фотографий из {len(files)}\n')
        bar.finish()
