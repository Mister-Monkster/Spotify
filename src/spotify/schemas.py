from pydantic import BaseModel


class STrackTop(BaseModel):
    id: str
    name: str
    album: str
    track_url: str
    album_url: str
    artists: dict[str, list[str]]

class STrack(STrackTop):
    image: str
    bar: str

class SProfile(BaseModel):
    name: str
    url: str
    image: str


class SArtist(BaseModel):
    id: str
    name: str
    followers: int
    popularity: int
    genres: list[str]
    image: str


class SAlbum(BaseModel):
    name: str
    user_name: str
    tracks_count: int
    url: str
    image: str