from flask import Flask, redirect, render_template, flash, g, session, request
from functools import wraps
from flask_debugtoolbar import DebugToolbarExtension
import musicbrainzngs as mb
import _startup
import os

from models import db, connect_db, User, Playlist, Recording, Tag
from forms import RegisterForm, LoginForm, EditRecordingForm, PlaylistForm, AddToPlaylistForm
from helpers import create_tag, get_recording_info, get_spotify_info, get_refresh_token
from sqlalchemy.exc import IntegrityError

CURR_USER_KEY = 'curr_user'
ACCESS_TOKEN = 'access_token'

TOKEN = ''

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///musophile')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
	app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'kepler-victoria')


# Set to false to stop debugger from intercepting redirects
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
debug = DebugToolbarExtension(app)

mb.set_useragent('Musophile', '0.1')
mb.set_format(fmt='json')

db.create_all()

###########
# Route helpers
###########

@app.before_request
def add_user_to_g():
    """Add logged-in user to Flask global to easily get user info"""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def login_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if g.user:
            return f(*args, **kwargs)
        else:
            flash("You must be logged in to do that.", 'warning')
            return redirect('/')
    return func

def do_login(user):
    """Login function"""
    session[CURR_USER_KEY] = user.id

###########
# Landing page and error pages
###########

@app.route('/')
def home_page():
    """Landing page"""
    return render_template('home.html')

@app.errorhandler(404)
def not_found(e):
    """404 page"""
    return render_template('404.html'), 404

###########
# Spotify auth routes
###########

@app.route('/auth')
def start_auth():
    response = _startup.getUser()
    return redirect(response)

@app.route('/callback/')
def auth_spotify():
    _startup.getUserToken(request.args['code'])
    return redirect('/search')

@app.route('/reauth')
def reauthorize_spotify():
    refresh_token = session[ACCESS_TOKEN][3]
    token = get_refresh_token(refresh_token)
    token.append(refresh_token)
    session[ACCESS_TOKEN] = token

    return {'reauth': True}

###########
# Basic user routes (login/registration/search)
###########

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        role = form.role.data
        img_url = form.img_url.data if form.img_url.data else None
        
        new_user = User.register(username, password, email, role, img_url)
        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            flash('There was something wrong with registration. Try a different username or email.', 'danger')
            return redirect('/register')

        do_login(new_user)
        flash("Account successfully created!", 'success')
        return redirect('/')
    else:
        return render_template('user/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user"""
    if g.user:
        flash("You're already logged in!", 'warning')
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Welcome back, {user.username}!", 'success')
            return redirect('/')
        
        flash("Invalid credentials", 'danger')
    
    return render_template('user/login.html', form=form)

@app.route('/logout', methods=['POST'])
def logout():
    """Log out of account"""
    session.pop(CURR_USER_KEY)
    flash("Goodbye for now!", 'primary')
    return redirect('/')

###########
# Authenticated user routes
###########

@app.route('/search')
@login_required
def search_page():
    """Search page"""
    token = _startup.getAccessToken()
    if token and (ACCESS_TOKEN not in session):
        session[ACCESS_TOKEN] = token
    return render_template('search.html')

@app.route('/search/api/<title>/<artist>')
@login_required
def get_info(title, artist):
    spotify_info = get_spotify_info(title, artist, session[ACCESS_TOKEN][0])

    if 'error' in spotify_info:
        if spotify_info['error']['status'] == 401:
            reauth = redirect('/reauth')
            return reauth

    return spotify_info

@app.route('/user/<int:user_id>')
@login_required
def user_page(user_id):
    """User page"""
    user = User.query.get_or_404(user_id)
    return render_template('user/user.html', user=user)

###########
# User library routes

@app.route('/user/<int:user_id>/library')
@login_required
def show_user_library(user_id):
    """Display the user library"""
    user = User.query.get_or_404(user_id)
    return render_template('user/library.html', user=user)

@app.route('/user/add-recording/<recording_id>/<spotify_uri>', methods = ['POST'])
@login_required
def add_recording_to_library(recording_id, spotify_uri):
    """Add a recording to user's library"""
    
    recording_data = get_recording_info(recording_id)

    recording = Recording(
        mbid = recording_id,
        title = recording_data['title'],
        artist = recording_data['artist'],
        release = recording_data['release'] if recording_data['release'] else None,
        spotify_uri = spotify_uri if spotify_uri != '0' else None
    )
    db.session.add(recording)
    db.session.commit()

    tags = recording_data['tags'] if recording_data['tags'] else None
    if tags:
        for tag in tags:
            create_tag(tag, recording)
    
    user = User.query.get(session[CURR_USER_KEY])
    user.library.append(recording)

    db.session.commit()
    flash(f'{recording.title} successfully added to your library!', 'success')
    return redirect(f'/user/{g.user.id}')

@app.route('/user/<int:user_id>/library/<int:recording_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_recording(user_id, recording_id):
    """Edit the information on a recording"""
    recording = Recording.query.get_or_404(recording_id)
    form = EditRecordingForm()
    if form.validate_on_submit():
        recording.comments = form.comments.data
        for tag in form.tags.data.split(', '):
            if tag not in [tag.name for tag in recording.tags]:
                create_tag(tag, recording)
        db.session.commit()
        flash(f'Successfully updated {recording.title} in your library!', 'success')
        return redirect(f'/user/{user_id}/library')
    
    return render_template('user/edit-recording.html', recording=recording, form=form)

@app.route('/user/<int:user_id>/library/<int:recording_id>/delete', methods=['POST'])
@login_required
def delete_recording(recording_id, user_id):
    """Remove a recording from a user's library"""
    recording = Recording.query.get_or_404(recording_id)

    db.session.delete(recording)
    db.session.commit()
    flash('Successfully removed!', 'success')
    return redirect(f'/user/{user_id}/library')

###########
# Playlist routes

@app.route('/user/<int:user_id>/playlists')
@login_required
def show_user_playlists(user_id):
    """Show a user's playlists"""
    user = User.query.get_or_404(user_id)
    return render_template('user/playlists.html', user=user)


@app.route('/playlists/<int:playlist_id>')
@login_required
def show_playlist(playlist_id):
    """Show a playlist"""
    playlist = Playlist.query.get(playlist_id)
    tags = []
    for recording in playlist.recordings:
        for tag in recording.tags:
            tags.append(tag)

    return render_template('playlist/playlist.html', playlist=playlist, tags=tags)

@app.route('/user/<int:user_id>/playlists/new', methods=['GET', 'POST'])
@login_required
def new_playlist(user_id):
    """Create a new playlist"""
    user = User.query.get_or_404(user_id)
    form = PlaylistForm()
    if form.validate_on_submit():
        
        name = form.name.data
        description = form.description.data
        
        new_playlist = Playlist(
            name = name,
            description = description,
            user_id = user_id
        )
        db.session.add(new_playlist)
        db.session.commit()

        flash(f'Playlist {new_playlist.name} successfully made', 'success')
        return redirect(f'/user/{user.id}')
    return render_template('playlist/new-playlist.html', user=user, form=form)

@app.route('/playlists/<int:playlist_id>/add', methods=['GET', 'POST'])
@login_required
def add_recording_to_playlist(playlist_id):
    """Add recording to a playlist"""
    playlist = Playlist.query.get_or_404(playlist_id)
    form = AddToPlaylistForm(obj=g.user)
    form.recording.choices = [(r.id, r.title) for r in g.user.library if r not in playlist.recordings]
    
    if form.validate_on_submit():
        recording = Recording.query.get_or_404(form.recording.data)
        playlist.recordings.append(recording)
        db.session.commit()
        
        flash(f'Successfully added {recording.title} to {playlist.name}', 'success')
        return redirect(f'/playlists/{playlist.id}')

    return render_template('playlist/add-to-playlist.html', playlist=playlist, form=form)

@app.route('/playlists/<int:playlist_id>/remove/<int:recording_id>', methods=['POST'])
@login_required
def remove_recording_from_playlist(playlist_id, recording_id):
    """Remove recording from playlist"""
    playlist = Playlist.query.get_or_404(playlist_id)
    recording = Recording.query.get_or_404(recording_id)
    playlist.recordings.remove(recording)
    db.session.commit()
    flash(f'Successfully removed recording from {playlist.name}', 'success')
    return redirect(f'/playlists/{playlist_id}')

@app.route('/playlists/<int:playlist_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_playlist(playlist_id):
    """Edit information about a playlist"""
    playlist = Playlist.query.get_or_404(playlist_id)
    form = PlaylistForm(obj=playlist)
    if form.validate_on_submit():
        playlist.name = form.name.data
        playlist.description = form.description.data
        db.session.commit()

        flash(f'Successfully edited {playlist.name}', 'success')
        return redirect(f'/playlists/{playlist.id}')

    return render_template('playlist/edit-playlist.html', playlist=playlist, form=form)

@app.route('/playlists/<int:playlist_id>/delete', methods=['POST'])
@login_required
def delete_playlist(playlist_id):
    """Delete a playlist"""
    playlist = Playlist.query.get_or_404(playlist_id)
    user = User.query.get_or_404(playlist.user_id)
    db.session.delete(playlist)
    db.session.commit()

    flash(f'Successfully deleted playlist', 'success')
    return redirect(f'/user/{user.id}')

###########
# Tag routes
###########

@app.route('/tags/<int:tag_id>')
@login_required
def show_songs_with_tag(tag_id):
    """Show all songs on the Musophile database with the tag"""
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tag.html', tag=tag)

@app.route('/tags/<int:tag_id>/remove/<int:recording_id>', methods=['POST'])
@login_required
def remove_tag(tag_id, recording_id):
    """Remove tag from a recording"""
    tag = Tag.query.get_or_404(tag_id)
    recording = Recording.query.get_or_404(recording_id)
    recording.tags.remove(tag)
    db.session.commit()
    flash(f'Successfully removed {tag.name} tag from {recording.title}', 'success')
    return redirect(f'/user/{g.user.id}/library')