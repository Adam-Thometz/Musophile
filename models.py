from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

DEFAULT_IMG_URL = 'https://www.seaside3ny.com/wp/wp-content/uploads/seaside3ny.com/2015/09/Camera-Shy.png'

def connect_db(app):
    """Connect to database"""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User model"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    role = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.Text, default=DEFAULT_IMG_URL)

    library = db.relationship('Recording', secondary='libraries', backref='user')
    playlists = db.relationship('Playlist')

    @classmethod
    def register(cls, username, password, email, role, img_url):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8, email=email, role=role, img_url=img_url)

    @classmethod
    def authenticate(cls, username, password):
        """Authenticate a user for logging in"""
        user = cls.query.filter_by(username=username).first()
        
        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Playlist(db.Model):
    """Playlist model"""

    __tablename__ = 'playlists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    recordings = db.relationship('Recording', secondary='playlist_recordings', backref='playlists')


class Recording(db.Model):
    """Recording model"""

    __tablename__ = 'recordings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mbid = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    artist = db.Column(db.String, nullable=False)
    release = db.Column(db.String)
    spotify_uri = db.Column(db.String)
    comments = db.Column(db.Text)

    tags = db.relationship('Tag', secondary='recording_tags', backref='recordings')


class Tag(db.Model):
    """Tag model"""

    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)


# Relationship models

class Library(db.Model):
    """User-Recording relationship. Representation of a user library"""
    
    __tablename__ = 'libraries'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    recording_id = db.Column(db.Integer, db.ForeignKey('recordings.id'), primary_key=True)

class PlaylistRecording(db.Model):
    """Playlist-Recording relationship"""

    __tablename__ = 'playlist_recordings'

    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), primary_key=True)
    recording_id = db.Column(db.Integer, db.ForeignKey('recordings.id'), primary_key=True)

class RecordingTag(db.Model):
    """Recording-Tag relationship"""

    __tablename__ = 'recording_tags'

    recording_id = db.Column(db.Integer, db.ForeignKey('recordings.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)