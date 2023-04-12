import requests


class VkUser:

    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_photos(self, user_id=None, count=5, album='profile'):
        photos_url = self.url + 'photos.get'
        photos_params = {
            'owner_id': user_id,
            'album_id': album,
            'rev': 0,
            'extended': 1,
            'photo_sizes': 1,
            'count': count if count < 1001 else 1000
        }
        res = requests.get(photos_url,
                           params={**self.params, **photos_params}).json()

        if res.get('error') is not None:
            print(f'Код ошибки: {res["error"]["error_code"]}')
            return None

        return res['response']['items']
