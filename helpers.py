import requests
import musicbrainzngs as mb

from models import db, Tag
from _flask_spotify_auth import refreshAuth

SPOTIFY_API_SEARCH = 'https://api.spotify.com/v1/search/'

def get_recording_info(id):
    """Helper function to get recording info"""
    recording = mb.get_recording_by_id(id, includes=['artists', 'releases', 'tags'])

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

def get_spotify_info(title, artist, token):
    params = {
        'q': f'{title} {artist}',
        'type': 'track',
        'limit': 1
    }
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    res = requests.get(f'{SPOTIFY_API_SEARCH}', params=params, headers=headers)
    
    return res.json()

def create_tag(tag, recording):
    try_tag = Tag.query.filter_by(name=tag).one_or_none()
    if try_tag:
        recording.tags.append(try_tag)
        db.session.commit()
    else:
        new_tag = Tag(name=tag)
        db.session.add(new_tag)
        db.session.commit()

        recording.tags.append(new_tag)
        db.session.commit()