# Credit for the code in this file:
##################
# Author: Greg VanOrt
# Title: Flask-Spotify-Auth
# Source: https://github.com/vanortg/Flask-Spotify-Auth
# Version: v0.2
# Original Publish Date: 29 Sept, 2018
# Access Date: 13 Aug, 2021
##################

from _flask_spotify_auth import getAuth, refreshAuth, getToken
from secret_codes import CLIENT_ID, CLIENT_SECRET

#Port and callback url can be changed or left to localhost:5000
PORT = "5000"
CALLBACK_URL = "http://localhost"

#Add needed scope from spotify user
SCOPE = "streaming"
#token_data will hold authentication header with access code, the allowed scopes, and the refresh countdown 
TOKEN_DATA = []


def getUser():
    return getAuth(CLIENT_ID, "{}:{}/callback/".format(CALLBACK_URL, PORT), SCOPE)

def getUserToken(code):
    global TOKEN_DATA
    TOKEN_DATA = getToken(code, CLIENT_ID, CLIENT_SECRET, "{}:{}/callback/".format(CALLBACK_URL, PORT))
 
def refreshToken(time):
    time.sleep(time)
    TOKEN_DATA = refreshAuth()

def getAccessToken():
    return TOKEN_DATA
