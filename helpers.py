import requests
from math import floor

from sqlalchemy.exc import IntegrityError
import musicbrainzngs as mb

from models import db, Tag
from _startup import TOKEN_DATA

MUSICBRAINZ_API_URL = 'https://musicbrainz.org/ws/2'
SPOTIFY_API_SEARCH = 'https://api.spotify.com/v1/search/'

def get_recording_info(id):
    """Helper function to get recording info"""
    recording = mb.get_recording_by_id(id, includes=['artists', 'releases', 'isrcs', 'tags'])

    title = recording['title']
    try:
        artist = recording['artist-credit'][0]['artist']['name']
    except IndexError:
        artist = 'N/A'
    try:
        release = recording['releases'][0]['title']
    except IndexError:
        release = 'N/A'
    tags = [tag['name'] for tag in recording['tags']]

    data = {
        'title': title,
        'artist': artist,
        'release': release,
        'tags': tags
    }

    return data

def create_tag(tag, target):
    try_tag = Tag.query.filter_by(name=tag).one_or_none()
    if try_tag:
        target.tags.append(try_tag)
        db.session.commit()
    else:
        new_tag = Tag(name=tag)
        db.session.add(new_tag)
        db.session.commit()

        target.tags.append(new_tag)
        db.session.commit()

def get_spotify_uri(title, artist):
    token = TOKEN_DATA[0]
    res = requests.get(f'{SPOTIFY_API_SEARCH}?q={title}+{artist}&type=track&limit=1', headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    })
    import pdb; pdb.set_trace()
    json = res.json()
    spotify_uri = json['tracks']['items'][0]['uri']
    return spotify_uri[14:]