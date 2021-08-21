"""Misc View tests."""

# run tests by typing in the terminal:
# python -m unittest test_app_rest.py

from unittest import TestCase

from app import app, CURR_USER_KEY
from models import  db, User, Recording, Playlist, Tag

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///musophile_test"
app.config['SQLALCHEMY_ECHO'] = False

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test user views"""
    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.u = User.register(
            username="Spongebob",
            password="gary1234",
            email="sponge@test.com",
            role="Other",
            img_url=None
        )
        self.r = Recording(
            mbid = '12345',
            title = 'F.U.N.',
            artist = 'Spongebob Squarepants',
            release = 'Spongebob Squarepants'
        )
        db.session.add_all([self.u, self.r])
        db.session.commit()

        self.u.library.append(self.r)
        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def setup_playlist(self):
        p = Playlist(
            name = 'Jelly Jamz',
            description = 'I like jellyfishing!',
            user_id = self.u.id
        )
        db.session.add(p)
        db.session.commit()

        p.recordings.append(self.r)
        db.session.commit()
    
    def setup_tag(self):
        t = Tag(name = 'peanut butter jelly time!')
        db.session.add(t)
        db.session.commit()
        
        self.r.tags.append(t)
        db.session.commit()

    # Playlist tests

    def test_show_user_playlists(self):
        """Do the user's playlists display?"""
        self.setup_playlist()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id
            resp = c.get(f'/user/{self.u.id}/playlists')
            html = str(resp.data)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Jelly Jamz', html)

    def test_show_playlist(self):
        """Does it show a specific playlist?"""
        self.setup_playlist()
        self.setup_tag()
        p = Playlist.query.get(1)
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id
            resp = c.get(f'/playlists/{p.id}')
            html = str(resp.data)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('I like jellyfishing!', html)
            self.assertIn('peanut butter jelly time!', html)

    def test_new_playlist(self):
        """Does it create a new playlist?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id
            resp = c.post(f'/user/{self.u.id}/playlists/new', data={
                'name': 'Krabby Patty music',
                'description': 'Work music'
            }, follow_redirects=True)
            html = str(resp.data)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Krabby Patty music', html)

    def test_add_recording_to_playlist(self):
        """Does it add a recording to a playlist?"""
        self.setup_playlist()
        r = Recording(
            mbid = '437uyn',
            title = 'Clarinet Concerto',
            artist = 'Squidward',
            release = 'The Artist Also Known As Squidward'
        )
        db.session.add(r)
        db.session.commit()

        self.u.library.append(r)
        db.session.commit()

        r = Recording.query.get(2)
        p = Playlist.query.get(1)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id
            resp = c.post(f'/playlists/{p.id}/add', data={'recording': 2}, follow_redirects=True)
            html = str(resp.data)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Clarinet Concerto', html)

    def test_remove_recording_from_playlist(self):
        """Does it remove a recording from a playlist?"""
        self.setup_playlist()
        r = Recording.query.get(1)
        p = Playlist.query.get(1)
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id
            resp = c.post(f'/playlists/{p.id}/remove/{r.id}', follow_redirects=True)
            html = str(resp.data)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Successfully removed recording from Jelly Jamz', html)

    def test_edit_playlist(self):
        """Does it edit a playlist?"""
        self.setup_playlist()
        p = Playlist.query.get(1)
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id
            resp = c.post(f'/playlists/{p.id}/edit', follow_redirects=True, data={
                'name': 'Jellyfish Jamz',
                'description': 'What a wonderful playlist!'
            })
            html = str(resp.data)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Jellyfish Jamz', html)

    def test_delete_playlist(self):
        """Does it delete a playlist?"""
        self.setup_playlist()
        p = Playlist.query.get(1)
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id
            resp = c.post(f'/playlists/{p.id}/delete', follow_redirects=True)
            html = str(resp.data)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Successfully deleted playlist', html)

    # Tag tests

    def test_show_tag(self):
        """Does it show a specific tag and its recordings?"""
        self.setup_tag()
        t = Tag.query.get(1)
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id
            resp = c.get(f'/tags/{t.id}')
            html = str(resp.data)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('peanut butter jelly time!', html)
            self.assertIn('F.U.N.', html)
    
    def remove_tag(self):
        """Does it remove a tag from a recording"""
        self.setup_tag()
        t = Tag.query.get(1)
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id
            resp = c.get(f'/tags/{t.id}/remove/{self.r.id}')
            html = str(resp.data)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Successfully removed peanut butter jelly time! tag from F.U.N.', html)
            self.assertIn('F.U.N.', html)