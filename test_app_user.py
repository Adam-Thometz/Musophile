"""User View tests."""

# run tests by typing in the terminal:
# python -m unittest test_app_user.py

from unittest import TestCase

from app import app, CURR_USER_KEY
from models import  db, User, Recording

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///musophile_test"
app.config['SQLALCHEMY_ECHO'] = False

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

TEST_GET_RECORDING = 'e8424e86-fafc-43a3-8577-c8a4c0a4456d'
TEST_SPOTIFY_URI = '0zNdw7vzK7nVtMlNkjVRfb'

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
        
        db.session.add(self.u)
        db.session.commit()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    # Basic user routes

    def test_homepage_no_user(self):
        """Does the navbar reflect the lack of logged in user?"""
        with self.client as c:
            resp = c.get('/')
            html = str(resp.data)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Welcome to Musophile!', html)
            self.assertIn('<b>Hello, stranger!</b>', html)

    def test_homepage_with_user(self):
        """Does the navbar show user buttons?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id
            resp = c.get('/')
            html = str(resp.data)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Welcome to Musophile!', html)
            self.assertIn('<b>Hello, Spongebob!</b>', html)

    def test_show_user(self):
        """Does a specific user show up?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id
            resp = c.get(f'/user/{self.u.id}')
            html = str(resp.data)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Spongebob', html)

    # User library routes

    def test_add_recording_to_library(self):
        """Is a new recording successfully displayed in a user's library?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id
            resp = c.post(f'/user/add-recording/{TEST_GET_RECORDING}/{TEST_SPOTIFY_URI}', follow_redirects=True)
            html = str(resp.data)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Title: Sweet Victory', html)
            self.assertIn('Artist: SpongeBob SquarePants', html)
    
    def setup_recording(self):
        """Set up recording model"""
        r = Recording(
            mbid = '12345',
            title = 'F.U.N.',
            artist = 'Spongebob Squarepants',
            release = 'Spongebob Squarepants',
        )
        db.session.add(r)
        db.session.commit()

        r = Recording.query.get(1)

        self.u.library.append(r)
        db.session.commit()

        return r.id

    def test_edit_recording(self):
        """Is a recording successfully edited?"""
        r_id = self.setup_recording()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id
            resp = c.post(f'/user/{self.u.id}/library/{r_id}/edit', data={
                'comments': 'Fun times!',
                'tags': 'fun, plankton'
            }, follow_redirects=True)
            html = str(resp.data)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Comments: Fun times!', html)
            self.assertIn('<a href="/tags/1">fun</a>', html)

    def test_delete_recording(self):
        """Is a recording successfully deleted?"""
        r_id = self.setup_recording()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id
            resp = c.post(f'/user/{self.u.id}/library/{r_id}/delete', follow_redirects=True)
            html = str(resp.data)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('F.U.N.', html)
            self.assertIn('Successfully removed!', html)