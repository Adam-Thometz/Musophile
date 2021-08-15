"""User model tests"""

# run tests by typing in terminal:
#    python -m unittest test_model_user.py

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, User, Recording, Playlist, DEFAULT_IMG_URL

os.environ['DATABASE_URL'] = "postgresql:///musophile_test"


db.create_all()

class UserModelTestCase(TestCase):
    """Test user model."""
    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.register('Spongebob', 'password', 'sponge@bikini-bottom.com', 'Music Fan', 'https://upload.wikimedia.org/wikipedia/en/3/3b/SpongeBob_SquarePants_character.svg')

        db.session.add(u1)
        db.session.commit()

        self.u1 = User.query.get(1)

        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    # Basic tests

    def test_user_model(self):
        """Basic model functionality?"""

        u = User(
            username="MrKrab$",
            password="money$$1234",
            email="mr-krabs@bikini-bottom.com",
            role="Music Producer",
            img_url=DEFAULT_IMG_URL
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(len(u.library), 0)
        self.assertEqual(len(u.playlists), 0)

    # Registration tests

    def test_register(self):
        """Test user sign up"""
        u_test = User.register('SandyCheeks', 'texas1234', 'sandy@bikini-bottom.com', 'Composer/Arranger', None)
        db.session.add(u_test)
        db.session.commit()

        u_test = User.query.get(2)

        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, 'SandyCheeks')
        self.assertEqual(u_test.email, 'sandy@bikini-bottom.com')
        self.assertEqual(u_test.role, 'Composer/Arranger')
        self.assertNotEqual(u_test.password, 'texas1234')
        self.assertTrue(u_test.password.startswith('$2b$'))

    def test_register_invalid_username(self):
        """Test invalid username"""
        u_test = User.register('Spongebob', 'texas1234', 'sandy@bikini-bottom.com', 'Composer/Arranger', None)
        with self.assertRaises(IntegrityError):
            db.session.add(u_test)
            db.session.commit()

    def test_register_invalid_email(self):
        """Test invalid email"""
        u_test = User.register('SandyCheeks', 'texas1234', 'sponge@bikini-bottom.com', 'Composer/Arranger', None)
        with self.assertRaises(IntegrityError):
            db.session.add(u_test)
            db.session.commit()
    
    # Authentication tests (login/Spotify)

    def test_authenticate(self):
        """Test successful authentication"""
        u_test = User.authenticate('Spongebob', 'password')
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.id, 1)
    
    def test_auth_invalid_username(self):
        """Test invalid username"""
        self.assertFalse(User.authenticate('plankton', 'password'))

    def test_auth_invalid_password(self):
        """Test invalid password"""
        self.assertFalse(User.authenticate('Spongebob', 'mayonaise_inst12'))


    # Functionality/relationship tests

    def test_user_library(self):
        """Test user library"""
        r = Recording(mbid = '12345', title = 'F.U.N.', artist = 'Spongebob Squarepants', release = 'Spongebob Squarepants')
        db.session.add(r)
        db.session.commit()

        self.r = Recording.query.get(1)
        
        self.u1.library.append(self.r)
        db.session.commit()

        self.assertEqual(len(self.u1.library), 1)
        self.assertEqual(self.u1.library[0].id, self.r.id)
    
    def test_user_playlist(self):
        """Test user playlist"""
        p = Playlist(name = "I'm ready!", description = "I'm ready. I'm ready. I'm ready. I'm ready. I'm ready. I'm ready.", user_id = 1)
        db.session.add(p)
        db.session.commit()

        self.p = Playlist.query.get(1)
        
        self.assertEqual(len(self.u1.playlists), 1)
        self.assertEqual(self.u1.playlists[0].id, self.p.id)