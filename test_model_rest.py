"""Misc model tests"""

# run tests by typing in the terminal:
# python -m unittest test_model_rest.py

from unittest import TestCase

from app import app
from models import db, Recording, User, Playlist, Tag, DEFAULT_IMG_URL

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///musophile_test"
app.config['SQLALCHEMY_ECHO'] = False

class RecordingModelTestCase(TestCase):
    """Test recording model."""
    def setUp(self):
        db.drop_all()
        db.create_all()

        r = Recording(mbid = '12345', title = 'F.U.N.', artist = 'Spongebob Squarepants', release = 'Spongebob Squarepants')
        db.session.add(r)
        db.session.commit()

        self.r = Recording.query.get(1)

        u = User(
            username="Gary-da-Snail$",
            password="meow1234",
            email="gary@bikini-bottom.com",
            role="Performer (vocals)",
            img_url=DEFAULT_IMG_URL
        )
        db.session.add(u)
        db.session.commit()

        self.u = User.query.get(1)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_recording_model(self):
        """Basic recording model functionality"""
        r = Recording(
            mbid = '245724676rttht',
            title = 'The Campfire Song',
            artist = 'Sponge & Pat',
            release = 'Fun Times'
        )
        db.session.add(r)
        db.session.commit()

        self.assertEqual(len(r.tags), 0)
        self.assertEqual(len(r.playlists), 0)
        self.assertEqual(len(r.user), 0)
    
    def test_playlist_model(self):
        """Basic playlist model functionality"""
        p = Playlist(
            name = "Gary's Jamz",
            description = "These are my favorite tunes to scratch Spongebob's sofas to.",
            user_id = self.u.id
        )
        db.session.add(p)
        db.session.commit()

        self.assertEqual(p.name, "Gary's Jamz")
        self.assertEqual(len(p.recordings), 0)

    def test_tag_model(self):
        """Basic tag model functionality"""
        t = Tag(
            name = "clarinet music",
        )
        db.session.add(t)
        db.session.commit()

        self.assertEqual(len(t.recordings), 0)

    # Recording relationships

    def test_recording_user_relationship(self):
        """Testing library relationship"""
        self.u.library.append(self.r)
        self.assertEqual(self.r.user, [self.u])
        self.assertEqual(len(self.u.library), 1)
        self.assertEqual(self.u.library[0].title, 'F.U.N.')
    
    def test_recording_playlist_relationship(self):
        """Testing recording-playlist relationship"""
        p = Playlist(name = 'Funness!', description = "I CAN'T STOP HAVING FUN!", user_id = self.u.id)
        db.session.add(p)
        db.session.commit()

        p.recordings.append(self.r)
        db.session.commit()

        self.assertEqual(len(self.r.playlists), 1)
        self.assertEqual(len(self.u.playlists), 1)
        self.assertEqual(self.u.playlists[0].name, 'Funness!')
    
    def test_recording_tag_relationship(self):
        t = Tag(name = 'pop')
        db.session.add(t)
        db.session.commit()

        self.r.tags.append(t)
        db.session.commit()

        self.assertEqual(len(self.r.tags), 1)
        self.assertEqual(len(t.recordings), 1)
        self.assertEqual(self.r.tags[0].name, 'pop')