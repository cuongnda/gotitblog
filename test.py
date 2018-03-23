import unittest
import os
import json

from flask_login import login_user

from app import create_app, db
from app.models import User


class BlogPostTestCase(unittest.TestCase):
    """This class represents the blog post test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.post = {'title': 'my very first post'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

            # Create a user to test
            self.fb_user = User(email="fb_user@example.com", type='facebook')
            self.gg_user = User(email="gg_user@example.com", type='google')
            db.session.add(self.fb_user)
            db.session.add(self.gg_user)
            db.session.commit()

    def test_user_creation(self):
        """TODO: We need to test user creation and user login with Facebook and Google Oauth"""

    def test_post_creation(self):
        """Test API can create a post (POST request)"""
        with self.client():
            query = User.query.filter_by(email=self.fb_user.email)
            fb_user = query.one()
            #login_user(self.fb_user)
            res = self.client().post('/posts/', data=self.post)
            self.assertEqual(res.status_code, 201)
            self.assertIn('my very first post', str(res.data))

    def test_api_can_get_all_posts(self):
        """Test API can get a post (GET request)."""
        res = self.client().post('/posts/', data=self.post)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/posts/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('my very first post', str(res.data))

    def test_api_can_get_post_by_id(self):
        """Test API can get a single post by using it's id."""
        rv = self.client().post('/posts/', data=self.post)
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/posts/{}'.format(result_in_json['id']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('my very first post', str(result.data))

    def test_post_can_be_edited(self):
        """Test API can edit an existing post. (PUT request)"""
        rv = self.client().post(
            '/posts/',
            data={'title': 'My very first post'})
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            '/posts/1',
            data={
                "title": "My very first post edited"
            })
        self.assertEqual(rv.status_code, 200)
        results = self.client().get('/posts/1')
        self.assertIn('edited', str(results.data))

    def test_post_deletion(self):
        """Test API can delete an existing post. (DELETE request)."""
        rv = self.client().post(
            '/posts/',
            data={'title': 'My very first post'})
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete('/posts/1')
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/posts/1')
        self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
