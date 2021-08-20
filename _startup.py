# Credit for the code (excluding deployment-related items) in this file:
##################
# Author: Greg VanOrt
# Title: Flask-Spotify-Auth
# Source: https://github.com/vanortg/Flask-Spotify-Auth
# Version: v0.2
# Original Publish Date: 29 Sept, 2018
# Access Date: 13 Aug, 2021
##################

from _flask_spotify_auth import getAuth, getToken
from boto.s3.connection import S3Connection
import os
# from secret_codes import CLIENT_ID, CLIENT_SECRET

PORT = "5000"
CALLBACK_URL = "https://musophile.herokuapp.com"
CLIENT_ID = S3Connection(os.environ['CLIENT_ID'])
CLIENT_SECRET = S3Connection(os.environ['CLIENT_SECRET'])
SCOPE = "user-read-private user-read-playback-state user-read-playback-position user-modify-playback-state user-read-email user-read-currently-playing"
TOKEN_DATA = []

def getUser():
    return getAuth(CLIENT_ID, "{}:{}/callback/".format(CALLBACK_URL, PORT), SCOPE)

def getUserToken(code):
    global TOKEN_DATA
    TOKEN_DATA = getToken(code, CLIENT_ID, CLIENT_SECRET, "{}:{}/callback/".format(CALLBACK_URL, PORT))

# This function, along with the refreshAuth function in _flask_spotify_auth, was rewritten into get_refresh_auth in the helper file

# def refreshToken(time):
#     time.sleep(time)
#     TOKEN_DATA = refreshAuth()

def getAccessToken():
    return TOKEN_DATA
