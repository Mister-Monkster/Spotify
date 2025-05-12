import requests


class TelegramService:
    def __init__(self):
        self.image_for_top = "https://cloudfront-us-east-1.images.arcpublishing.com/infobae/YPKERJYVRZBXHGJUI4WSWFUTVA.jpg"
        self.image_playlists = "https://media.gq-magazine.co.uk/photos/671ba4d69bcde28d0eb32470/3:2/w_1620,h_1080,c_limit/spotify-playlists.jpg"

    @staticmethod
    async def start(user_id):
        res = requests.post(f'http://127.0.0.1:8000/login/{user_id}').json()
        return res['link']

    @staticmethod
    async def track(user_id):
        res = requests.get(f'http://127.0.0.1:8000/current-track/{user_id}')
        if res.status_code == 404:
            return 404
        res = res.json()
        artists = []
        for artist in res['artists'].values():
            artist_str = f'<i><a href="{artist[1]}">{artist[0]}</a></i>'
            artists.append(artist_str)
        current_track_text = (f'<a href="{res["image"]}">&#8203;</a>\n'
                              f'<b>🔈Track</b> <i><a href="{res['track_url']}">{res['name']}</a></i>\n'
                              f'<b>💿Album</b> <i><a href="{res['album_url']}">{res['album']}</a></i>\n'
                              f"<b>🎙Artists</b> <i>{', '.join(artists)}</i>\n"
                              f"<code><i>{res['bar']}</i></code>")
        return current_track_text


    async def top_tracks(self, user_id):
        res = requests.get(f'http://127.0.0.1:8000/top-tracks/{user_id}').json()
        if not res:
            return 404
        text = (
            f'<a href="{self.image_for_top}">&#8203;</a>\n'
            f'<b>Вот твой топ треков за месяц:</b>\n\n')
        place = 1
        for item in res:
            artists = []
            for artist in item['artists'].values():
                artist_str = f'<i><a href="{artist[1]}">{artist[0]}</a></i>'
                artists.append(artist_str)
            track_text = (
                          f'<b>Place <i>{place}</i></b>\n'
                          f'<b>Track</b> <i><a href="{item['track_url']}">{item["name"]}</a></i>\n'
                          f'<b>Album</b> <i><a href="{item['album_url']}">{item["album"]}</a></i>\n'
                          f'<b>Artists</b> <i>{", ".join(artists)}</i>\n\n')
            text += track_text
            place += 1
        return text

    async def top_artists(self, user_id):
        res = requests.get(f'http://127.0.0.1:8000/top-artists/{user_id}').json()
        if not res:
            return 404
        text = (f'<a href="{self.image_for_top}">&#8203;</a>\n'
                f'<b>Вот твой топ артистов за месяц:</b>\n\n')
        place = 1
        for item in res:
            artist_text = (
                           f'<b>Place <i>{place}</i></b>\n'
                           f'<b>{item["name"]}</b>\n'
                           f'Подписчиков: <i>{item["followers"]}</i>\n'
                           f'Популярность: <i>{item["popularity"]}</i>\n\n')
            text += artist_text
            place += 1
        return text

    async def playlists(self, user_id):
        res = requests.get(f'http://127.0.0.1:8000/albums/{user_id}').json()
        if not res:
            return 404
        text = (f'<a href="{self.image_playlists}">&#8203;</a>\n'
                '<b>Вот список ваших плейлистов</b>\n\n')
        for item in res:
            text += f'<b>Название: </b><i><a href="{item['url']}">{item["name"]}</a></i>\n'
            text += f'<b>Пользователь: </b><i>{item["user_name"]}</i>\n'
            text += f'<b>Треков: </b><i>{item["tracks_count"]}</i>\n\n'

        return text

    async def me(self, user_id):
        res = requests.get(f'http://127.0.0.1:8000/current-user/{user_id}').json()
        if not res:
            return 404
        text = (f'<a href="{res['image']}">&#8203;</a>\n'
                f'Вот ваш профиль Spotify\n'
                f'<a href="{res['url']}">{res['name']}</a>')
        return text

    async def logout(self, user_id):
        res = requests.delete(f'http://127.0.0.1:8000/logout/{user_id}').json()
        if not res['ok']:
            return False
        return res


