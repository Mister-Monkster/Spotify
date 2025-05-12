from fastapi import APIRouter, HTTPException
from starlette.responses import RedirectResponse

from spotify.deps import ServiceDep
from spotify.schemas import STrack, SProfile, SArtist, SAlbum, STrackTop

router = APIRouter()

@router.post('/login/{tg_id}')
async def login(tg_id: int, service: ServiceDep):
    link = await service.get_auth_link(tg_id)
    print(link)
    return {'link': link}


@router.get('/callback')
async def callback(code: str, state: str, service: ServiceDep):
    user_id = state
    await service.get_token(user_id, code)
    return RedirectResponse('https://t.me/SpotfyTranslatorBot', status_code=301)


@router.get('/current-track/{tg_id}')
async def current_track(tg_id: str, service: ServiceDep) -> STrack:
    track = await service.get_user_current_track(tg_id)
    if track is None:
        raise HTTPException(status_code=404)
    return track


@router.get('/current-user/{tg_id}')
async def profile(tg_id: str, service: ServiceDep) -> SProfile | None:
    try:
        profile = await service.profile(tg_id)
        return profile
    except Exception as e:
        print(e)


@router.get('/top-tracks/{tg_id}')
async def top_tracks(tg_id: str, service: ServiceDep) -> list[STrackTop] | None:
    try:
        tracks = await service.get_top_tracks(tg_id)
        if tracks is None:
            raise HTTPException(status_code=404)
        return tracks
    except Exception as e:
        print(e)


@router.get('/top-artists/{tg_id}')
async def top_artists(tg_id: str, service: ServiceDep) -> list[SArtist] | None:
    try:
        artists = await service.get_top_artists(tg_id)
        return artists
    except Exception as e:
        print(e)


@router.get('/albums/{tg_id}')
async def albums(tg_id: str, service: ServiceDep) -> list[SAlbum] | None:
    albums = await service.get_albums(tg_id)
    if albums is None:
        raise HTTPException(status_code=404)
    return albums


@router.delete('/logout/{tg_id}')
async def logout(tg_id: str, service: ServiceDep):
    try:
        await service.logout(tg_id)
        return {'ok': True, 'detail': 'Logout successful'}
    except:
        return {'ok': False, 'detail': 'Logout failed'}