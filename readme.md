# Musophile

###### Developer: Adam Thometz

Link to Musophile:

Description: A website where users can create playlists of Spotify songs. The tags that come with each recording are used to classify both recordings and playlists and users can find new songs by following the tags. Musophile is designed for music connoisseurs and people who work in music, such as musicians, DJs, academics, music teachers, etc.

### Features:
- **Search for songs on MusicBrainz database**: The search function of the website gets data from MusicBrainz, an open-source database for all things music-related, like a Wikipedia for music. The search query returns recording title, artist, release, and associated tags that are already found on MusicBrainz.
- **Attach Spotify recordings by title and artist**: If a result from the MusicBrainz database has an associated recording on Spotify, the Musophile API gets Spotify information according to title and artist information (release information is omitted from search in order to increase the likelihood of Spotify's GET request returning a usable recording).
- **Search website by tag**: Tags are categorically similar to genres. A user can easily search for recordings of the same tag in the Musophile database simply by clicking on the tag. The results will show all songs with the same tag and the user can add these recordings to their library.
    - *Please note that adding a recording from the tag list duplicates the song in the Musophile database. This was done intentionally in order to avoid users accidentally writing over comments or tags since they'd both be referencing the same entry in the recording table. Workarounds are welcome.*
    
### Basic user flow:
1. User must create a Musophile account in order to use the website. This makes it easier to authenticate the user's Spotify account, which is also required to use the site. A MusicBrainz account is not necessary at the moment.
2. After registering, the user can start searching for music. Before searching, the user is prompted to authenticate Spotify so that Musophile can make calls on the user's behalf. The user may then search by recording name, artist, release, or tag and start adding recordings to their library.
3. From there, the user can start making playlists, adding tags to their recordings, add comments to a recording if they wish, etc.
4. After one hour, Spotify will need to be reauthorized with a refresh token. This should be automatically handled by Musophile's server.

### APIs used: 
1. MusicBrainz:
    - Root URL: https://musicbrainz.org/ws/2/
    - [Docs](https://musicbrainz.org/doc/MusicBrainz_API)
2. Spotify
    - Root URL: https://api.spotify.com/v1
    - [Docs](https://developer.spotify.com/documentation/web-api/reference/)
    - **You must have a Spotify account in order to use Musophile**
    
### Tech stack:
- Front-end: HTML, CSS, JS, jQuery, Axios, Bootstrap
- Backend: Python, Flask, WTForms, musicbrainzngs, requests, Bcrypt
- Database: SQLAlchemy

To access required tools, run the following in terminal:

`python3 -m venv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`


Then run the server by typing `flask run`

### Possible features to add:
- **Searching Musophile by tag**: Instead of clicking on tags, users can search by tag in the Musophile database instead of clicking on tags of recordings that the user happens to find while browsing the site.
- **Create Spotify playlists**: A user can take their Musophile playlists and replicate them on their own Spotify account.
- **Finding people on Musophile with similar roles**: Users can connect with others who share similar music-related interests.
- **Sharing playlists**: Related to the above feature, users can share their playlists with other users on the site.
- **Contribute to Musicbrainz**: Since MusicBrainz is open-source, users could potentially make their own contributions to the MB database through Musophile, thereby strengthening its search capabilities.