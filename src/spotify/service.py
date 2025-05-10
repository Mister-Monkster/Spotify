import json
import os
from typing import Optional, List

import spotipy
from redis.asyncio import Redis
from spotipy import SpotifyOAuth
from spotipy.exceptions import SpotifyException

from config import get_secrets
from spotify.schemas import STrack, SProfile, SArtist, SAlbum, STrackTop


class SpotifyService:
    def __init__(self, redis: Redis):
        """
        Инициализирует сервис Spotify.

        Args:
            redis: Объект Redis для кэширования токенов.
        """
        self.scope = "user-read-currently-playing user-read-playback-state user-top-read"
        self.secrets = get_secrets()
        self.redirect_uri = os.getenv('REDIRECT_URI')
        self.redis = redis

    async def ms_to_str(self, ms: int) -> str:
        """
        Преобразует миллисекунды в строку формата MM:SS.
        """
        total_seconds = ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    async def format_progress_bar(self, position: int, total: int, bar_length: int = 10) -> str:
        """
        Форматирует прогресс-бар из символов.
        """
        if total <= 0:
            return "0:00 / 0:00"
        percentage = (position / total) * 100
        filled_chars = int(percentage / 100 * bar_length)
        bar = '🟢' * (filled_chars - 1) + '🔘' + '⚫️' * (bar_length - filled_chars)
        current_time = await self.ms_to_str(position)
        total_time = await self.ms_to_str(total)
        return f"{current_time} {bar} {total_time}"

    async def parse_track(self, track: dict) -> dict:
        """
        Извлекает и форматирует информацию о треке из ответа Spotify API.
        """
        track_id = track['id']
        name = track['name']
        track_url = track['external_urls']['spotify']
        album = track['album']['name']
        album_url = track['album']['images'][0]['url']
        artists_dict = {
            f'artist_{i + 1}': [artist['name'], artist['external_urls']['spotify']]
            for i, artist in enumerate(track['artists'])
        }
        image = track['album']['images'][0]['url']
        return {
            'id': track_id,
            'name': name,
            'track_url': track_url,
            'album': album,
            'album_url': album_url,
            'artists': artists_dict,
            'image': image,
        }

    async def parse_artists(self, artist: dict) -> dict:
        """
        Извлекает и форматирует информацию об артисте из ответа Spotify API.
        """
        artist_id = artist['id']
        artist_name = artist['name']
        popularity = artist['popularity']
        followers = artist['followers']['total']
        genres = artist['genres']
        image = artist['images'][0]['url']
        return {
            'id': artist_id,
            'name': artist_name,
            'popularity': popularity,
            'followers': followers,
            'genres': genres,
            'image': image,
        }

    async def get_spotify_client(self, user_id: str) -> spotipy.Spotify:
        """
        Возвращает объект клиента Spotify, используя кэшированные токены или выполняя аутентификацию.
        """
        try:
            token_info = await self.redis.get(user_id)
            if token_info:
                token = json.loads(token_info)
                auth_manager = SpotifyOAuth(
                    client_id=self.secrets['client_id'],
                    client_secret=self.secrets['client_secret'],
                    redirect_uri=self.redirect_uri,
                    state=user_id,
                    cache_path=f".cache-{user_id}",
                )
                sp = spotipy.Spotify(auth=token['access_token'])
                if auth_manager.is_token_expired(token):
                    token_info = await self.refresh_token(user_id, auth_manager)
                    sp = spotipy.Spotify(auth=token_info['access_token'])
                return sp
            else:
                auth_manager = SpotifyOAuth(
                    scope=self.scope,
                    client_id=self.secrets['client_id'],
                    client_secret=self.secrets['client_secret'],
                    redirect_uri=self.redirect_uri,
                    state=user_id,
                    cache_path=f".cache-{user_id}",
                )
                return spotipy.Spotify(auth_manager=auth_manager)
        except Exception as e:
            print(f"Error getting Spotify client: {e}")
            raise

    async def refresh_token(
            self, user_id: str, auth_manager: SpotifyOAuth
    ) -> dict:  # Add auth_manager
        """
        Обновляет токен доступа Spotify и сохраняет его в Redis.
        """
        token_info = await self.redis.get(user_id)
        if token_info:
            token = json.loads(token_info)
            refresh_token = token.get('refresh_token')
            if refresh_token:
                try:
                    new_token_info = auth_manager.refresh_access_token(refresh_token)
                    await self.redis.set(
                        user_id,
                        json.dumps(new_token_info),
                        ex=new_token_info['expires_in'],
                    )
                    return new_token_info
                except SpotifyException as e:
                    print(f"Error refreshing token: {e}")

                    await self.redis.delete(user_id)
                    return {}
            else:
                print(f"Error: no refresh token found for user {user_id}")
                await self.redis.delete(user_id)
                return {}
        else:
            print(f"Error: no token info found for user {user_id}")
            return {}

    async def get_auth_link(self, user_id: str) -> str:
        """
        Возвращает ссылку для авторизации пользователя в Spotify.
        """
        sp = await self.get_spotify_client(user_id)
        auth_url = sp.auth_manager.get_authorize_url(state=user_id)
        return auth_url

    async def get_token(self, user_id: str, code: str) -> dict:
        """
        Получает токен доступа Spotify по коду авторизации и сохраняет его в Redis.
        """
        sp = await self.get_spotify_client(user_id)
        token_info = sp.auth_manager.get_access_token(code=code)
        await self.redis.set(user_id, json.dumps(token_info), ex=token_info['expires_in'])
        return token_info

    async def get_user_current_track(self, user_id: str) -> Optional[STrack]:
        """
        Возвращает информацию о текущем проигрываемом треке пользователя.
        """
        sp = await self.get_spotify_client(user_id)
        try:
            track = sp.current_user_playing_track()
        except spotipy.SpotifyException as e:
            print(f"Error getting current track: {e}")
            return None

        if not track or not track['item']:
            return None

        track_dict = await self.parse_track(track['item'])
        duration = track['item']['duration_ms']
        progress = track['progress_ms']
        bar = await self.format_progress_bar(progress, duration)
        track_dict['bar'] = bar
        return STrack.model_validate(track_dict)

    async def profile(self, user_id: str) -> SProfile:
        """
        Возвращает информацию о профиле пользователя Spotify.
        """
        sp = await self.get_spotify_client(user_id)
        current_user = sp.current_user()
        profile = {
            'name': current_user['display_name'],
            'url': current_user['external_urls']['spotify'],
            'image': current_user['images'][0]['url'],
        }
        return SProfile.model_validate(profile)

    async def get_top_tracks(self, user_id: str) -> Optional[List[STrackTop]]:
        """
        Возвращает список топ-треков пользователя.
        """
        sp = await self.get_spotify_client(user_id)
        try:
            top = sp.current_user_top_tracks(limit=10, offset=0, time_range='short_term')
        except spotipy.SpotifyException as e:
            print(f"Error getting top tracks: {e}")
            return None
        res = []
        for track in top['items']:
            track_dict = await self.parse_track(track)
            res.append(STrackTop.model_validate(track_dict))
        return res

    async def get_top_artists(self, user_id: str) -> Optional[List[SArtist]]:
        """
        Возвращает список топ-исполнителей пользователя.
        """
        sp = await self.get_spotify_client(user_id)
        try:
            top = sp.current_user_top_artists(limit=10, offset=0, time_range='short_term')
        except spotipy.SpotifyException as e:
            print(f"Error getting top artists: {e}")
            return None
        res = []
        for artist in top['items']:
            artist_dict = await self.parse_artists(artist)
            res.append(SArtist.model_validate(artist_dict))
        return res

    async def get_albums(self, user_id: str) -> Optional[List[SAlbum]]:
        """
        Возвращает список альбомов пользователя.
        """
        sp = await self.get_spotify_client(user_id)
        try:
            albums = sp.current_user_playlists()
        except spotipy.SpotifyException as e:
            print(f"Error getting user playlists: {e}")
            return None
        res = []
        for item in albums['items']:
            album_dict = {
                'name': item['name'],
                "user_name": item['owner']['display_name'],
                'tracks_count': item['tracks']['total'],
                "url": item['external_urls']['spotify'],
                "image": item['images'][0]['url'],
            }
            res.append(SAlbum.model_validate(album_dict))
        return res
