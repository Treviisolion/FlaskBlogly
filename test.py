from unittest import TestCase
from app import app, db, User, Post, DEFAULT_IMAGE

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///bloglytest'
app.config['SQLALCHEMY_ECHO'] = False

TEST_IMAGE = 'https://homepages.cae.wisc.edu/~ece533/images/airplane.png'


class FlaskTests(TestCase):
    """Tests the routes in app.py"""

    def setUp(self):
        """Recreates the tables for a fresh start and populates them with a single user and post"""

        # Creates empty tables
        db.drop_all()
        db.create_all()

        # Adds a single user
        new_user = User(first_name='John', last_name='Doe')
        db.session.add(new_user)
        db.session.commit()

        # Adds a single post to new_user
        new_post = Post(title='A Test', content='Testing posts', user_id=1)
        db.session.add(new_post)
        db.session.commit()

    def tearDown(self):
        """Clear any fouled transactions"""
        db.session.rollback()

    def test_redirect_home_page(self):
        with app.test_client() as client:
            resp = client.get('/')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/users')

    def test_get_default_img(self):
        with app.test_client() as client:
            resp = client.get(DEFAULT_IMAGE)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.content_type, 'image/png')

    def test_main_page(self):
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)
            self.assertIn('<li><a href="/users/1">John Doe</a></li>', html)
            self.assertIn('href="/users/new"', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_user_page(self):
        with app.test_client() as client:
            resp = client.get('/users/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>John Doe</h1>', html)
            self.assertIn('<li><a href="/posts/1">A Test</a></li>', html)
            self.assertIn('href="/users"', html)
            self.assertIn('href="/users/1/edit"', html)
            self.assertIn('href="/users/1/posts/new"', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_non_user_page(self):
        with app.test_client() as client:
            resp = client.get('/users/2')

            self.assertEqual(resp.status_code, 404)

    def test_non_user_page2(self):
        with app.test_client() as client:
            resp = client.get('/users/a')

            self.assertEqual(resp.status_code, 404)

    def test_new_user_form(self):
        with app.test_client() as client:
            resp = client.get('/users/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Create a User</h1>', html)
            self.assertIn('href="/users"', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_sucessful_new_user(self):
        with app.test_client() as client:
            resp = client.post(
                '/users/new', data={'first_name': 'Jane', 'last_name': 'Doe'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/users')

            user = User.query.get_or_404(2)
            self.assertEqual('Jane', user.first_name)
            self.assertEqual('Doe', user.last_name)
            self.assertEqual(DEFAULT_IMAGE, user.image_url)

            resp2 = client.get('/users')
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)
            self.assertIn('<li><a href="/users/1">John Doe</a></li>', html)
            self.assertIn('<li><a href="/users/2">Jane Doe</a></li>', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_sucessful_new_user_with_image(self):
        with app.test_client() as client:
            resp = client.post(
                '/users/new', data={'first_name': 'Bob', 'last_name': 'Builder', 'image_url': TEST_IMAGE})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/users')

            user = User.query.get_or_404(2)
            self.assertEqual('Bob', user.first_name)
            self.assertEqual('Builder', user.last_name)
            self.assertEqual(TEST_IMAGE, user.image_url)

            resp2 = client.get('/users')
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)
            self.assertIn('<li><a href="/users/1">John Doe</a></li>', html)
            self.assertIn('<li><a href="/users/2">Bob Builder</a></li>', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_missing_first_name(self):
        with app.test_client() as client:
            resp = client.post(
                '/users/new', data={'last_name': 'Noname', 'image_url': TEST_IMAGE})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Create a User</h1>', html)
            self.assertNotIn('WARNINGS GO HERE', html)
            self.assertIn(
                '<div class="alert alert-danger" role="alert">First name is required</div>', html)
            self.assertNotIn(
                '<div class="alert alert-danger" role="alert">Last name is required</div>', html)

    def test_missing_last_name(self):
        with app.test_client() as client:
            resp = client.post(
                '/users/new', data={'first_name': 'Noname', 'image_url': TEST_IMAGE})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Create a User</h1>', html)
            self.assertNotIn('WARNINGS GO HERE', html)
            self.assertNotIn(
                '<div class="alert alert-danger" role="alert">First name is required</div>', html)
            self.assertIn(
                '<div class="alert alert-danger" role="alert">Last name is required</div>', html)

    def test_edit_user_form(self):
        with app.test_client() as client:
            resp = client.get('/users/1/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Edit User</h1>', html)
            self.assertIn('href="/users/1"', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_edit_non_user(self):
        with app.test_client() as client:
            resp = client.get('/users/2/edit')

            self.assertEqual(resp.status_code, 404)

    def test_edit_non_user2(self):
        with app.test_client() as client:
            resp = client.get('/users/a/edit')

            self.assertEqual(resp.status_code, 404)

    def test_edit_user_first_name(self):
        with app.test_client() as client:
            resp = client.post('/users/1/edit', data={'first_name': 'James'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/users')

            resp2 = client.get('/users')
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)
            self.assertIn('<li><a href="/users/1">James Doe</a></li>', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_edit_user_last_name(self):
        with app.test_client() as client:
            resp = client.post('/users/1/edit', data={'last_name': 'Smith'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/users')

            resp2 = client.get('/users')
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)
            self.assertIn('<li><a href="/users/1">John Smith</a></li>', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_edit_user_full_name(self):
        with app.test_client() as client:
            resp = client.post(
                '/users/1/edit', data={'first_name': 'James', 'last_name': 'Smith'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/users')

            resp2 = client.get('/users')
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)
            self.assertIn('<li><a href="/users/1">James Smith</a></li>', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_edit_user_image_url(self):
        with app.test_client() as client:
            resp = client.post('/users/1/edit', data={'image_url': TEST_IMAGE})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/users')

            user = User.query.get_or_404(1)
            self.assertEqual(TEST_IMAGE, user.image_url)

            resp2 = client.get('/users')
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)
            self.assertIn('<li><a href="/users/1">John Doe</a></li>', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_edit_user_image_url_and_first_name(self):
        with app.test_client() as client:
            resp = client.post(
                '/users/1/edit', data={'first_name': 'James', 'image_url': TEST_IMAGE})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/users')

            user = User.query.get_or_404(1)
            self.assertEqual(TEST_IMAGE, user.image_url)

            resp2 = client.get('/users')
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)
            self.assertIn('<li><a href="/users/1">James Doe</a></li>', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_edit_user_image_url_and_first_name(self):
        with app.test_client() as client:
            resp = client.post(
                '/users/1/edit', data={'last_name': 'Smith', 'image_url': TEST_IMAGE})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/users')

            user = User.query.get_or_404(1)
            self.assertEqual(TEST_IMAGE, user.image_url)

            resp2 = client.get('/users')
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)
            self.assertIn('<li><a href="/users/1">John Smith</a></li>', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_edit_user_image_url_and_full_name(self):
        with app.test_client() as client:
            resp = client.post(
                '/users/1/edit', data={'first_name': 'James', 'last_name': 'Smith', 'image_url': TEST_IMAGE})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/users')

            user = User.query.get_or_404(1)
            self.assertEqual(TEST_IMAGE, user.image_url)

            resp2 = client.get('/users')
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)
            self.assertIn('<li><a href="/users/1">James Smith</a></li>', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_edit_non_user_post(self):
        with app.test_client() as client:
            resp = client.post(
                '/users/2/edit', data={'first_name': 'James', 'last_name': 'Smith', 'image_url': TEST_IMAGE})

            self.assertEqual(resp.status_code, 404)

    def test_edit_non_user_post2(self):
        with app.test_client() as client:
            resp = client.post(
                '/users/a/edit', data={'first_name': 'James', 'last_name': 'Smith', 'image_url': TEST_IMAGE})

            self.assertEqual(resp.status_code, 404)

    def test_delete_user(self):
        with app.test_client() as client:
            resp = client.post('/users/1/delete')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/users')

            posts = Post.query.all()
            users = User.query.all()
            self.assertEqual(len(posts), 0)
            self.assertEqual(len(users), 0)

            resp2 = client.get('/users')
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)
            self.assertNotIn(
                '<li><a href="/users/1">John Smith</a></li>', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_delete_non_user(self):
        with app.test_client() as client:
            resp = client.post('/users/2/delete')

            self.assertEqual(resp.status_code, 404)

    def test_delete_non_user2(self):
        with app.test_client() as client:
            resp = client.post('/users/a/delete')

            self.assertEqual(resp.status_code, 404)

    def test_new_post_form(self):
        with app.test_client() as client:
            resp = client.get('/users/1/posts/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Add a Post for John Doe</h1>', html)
            self.assertIn('href="/users/1"', html)
            self.assertNotIn('WARNINGS GO HERE', html)
            self.assertNotIn(
                '<div class="alert alert-danger" role="alert">Title is required</div>', html)
            self.assertNotIn(
                '<div class="alert alert-danger" role="alert">Some content is required</div>', html)

    def test_new_post_for_non_user(self):
        with app.test_client() as client:
            resp = client.get('/users/2/posts/new')

            self.assertEqual(resp.status_code, 404)

    def test_new_post_for_non_user(self):
        with app.test_client() as client:
            resp = client.get('/users/a/posts/new')

            self.assertEqual(resp.status_code, 404)

    def test_successful_new_post(self):
        with app.test_client() as client:
            resp = client.post(
                '/users/1/posts/new', data={'title': 'A second Test', 'content': 'More CONTENT!!!'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/users/1')

            post = Post.query.get_or_404(2)
            self.assertEqual('More CONTENT!!!', post.content)

            resp2 = client.get('/users/1')
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h1>John Doe</h1>', html)
            self.assertIn('<li><a href="/posts/1">A Test</a></li>', html)
            self.assertIn(
                '<li><a href="/posts/2">A second Test</a></li>', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_missing_title(self):
        with app.test_client() as client:
            resp = client.post('/users/1/posts/new',
                               data={'content': 'More CONTENT!!!'})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Add a Post for John Doe</h1>', html)
            self.assertNotIn('WARNINGS GO HERE', html)
            self.assertIn(
                '<div class="alert alert-danger" role="alert">Title is required</div>', html)
            self.assertNotIn(
                '<div class="alert alert-danger" role="alert">Some content is required</div>', html)

    def test_missing_content(self):
        with app.test_client() as client:
            resp = client.post('/users/1/posts/new',
                               data={'title': 'A second Test'})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Add a Post for John Doe</h1>', html)
            self.assertNotIn('WARNINGS GO HERE', html)
            self.assertNotIn(
                '<div class="alert alert-danger" role="alert">Title is required</div>', html)
            self.assertIn(
                '<div class="alert alert-danger" role="alert">Some content is required</div>', html)

    def test_missing_title_and_content(self):
        with app.test_client() as client:
            resp = client.post('/users/1/posts/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Add a Post for John Doe</h1>', html)
            self.assertNotIn('WARNINGS GO HERE', html)
            self.assertIn(
                '<div class="alert alert-danger" role="alert">Title is required</div>', html)
            self.assertIn(
                '<div class="alert alert-danger" role="alert">Some content is required</div>', html)

    def test_add_post_for_non_user(self):
        with app.test_client() as client:
            resp = client.post(
                '/users/2/posts/new', data={'title': 'A second Test', 'content': 'More CONTENT!!!'})

            self.assertEqual(resp.status_code, 404)

    def test_add_post_for_non_user2(self):
        with app.test_client() as client:
            resp = client.post(
                '/users/a/posts/new', data={'title': 'A second Test', 'content': 'More CONTENT!!!'})

            self.assertEqual(resp.status_code, 404)

    def test_post_page(self):
        with app.test_client() as client:
            resp = client.get('/posts/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>A Test</h1>', html)
            self.assertIn('<p>Testing posts</p>', html)
            self.assertIn('<i>By John Doe</i>', html)
            self.assertIn('href="/users/1"', html)
            self.assertIn('href="/posts/1/edit"', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_non_post_page(self):
        with app.test_client() as client:
            resp = client.get('/posts/2')

            self.assertEqual(resp.status_code, 404)

    def test_non_post_page2(self):
        with app.test_client() as client:
            resp = client.get('/posts/a')

            self.assertEqual(resp.status_code, 404)

    def test_edit_post_form(self):
        with app.test_client() as client:
            resp = client.get('/posts/1/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Edit Post</h1>', html)
            self.assertIn('href="/users/1"', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_edit_non_post(self):
        with app.test_client() as client:
            resp = client.get('/posts/2/edit')

            self.assertEqual(resp.status_code, 404)

    def test_edit_non_post(self):
        with app.test_client() as client:
            resp = client.get('/posts/a/edit')

            self.assertEqual(resp.status_code, 404)

    def test_edit_post_title(self):
        with app.test_client() as client:
            resp = client.post(
                '/posts/1/edit', data={'title': 'Something Different'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/posts/1')

            resp2 = client.get('/posts/1')
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h1>Something Different</h1>', html)
            self.assertIn('<p>Testing posts</p>', html)
            self.assertIn('<i>By John Doe</i>', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_edit_post_content(self):
        with app.test_client() as client:
            resp = client.post(
                '/posts/1/edit', data={'content': 'Almost not repetitive!'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/posts/1')

            resp2 = client.get('/posts/1')
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h1>A Test</h1>', html)
            self.assertIn('<p>Almost not repetitive!</p>', html)
            self.assertIn('<i>By John Doe</i>', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_edit_post_title_and_content(self):
        with app.test_client() as client:
            resp = client.post(
                '/posts/1/edit', data={'title': 'Something Different', 'content': 'Almost not repetitive!'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/posts/1')

            resp2 = client.get('/posts/1')
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h1>Something Different</h1>', html)
            self.assertIn('<p>Almost not repetitive!</p>', html)
            self.assertIn('<i>By John Doe</i>', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_edit_non_post_post(self):
        with app.test_client() as client:
            resp = client.post(
                '/posts/2/edit', data={'title': 'Something Different', 'content': 'Almost not repetitive!'})

            self.assertEqual(resp.status_code, 404)

    def test_edit_non_post_post2(self):
        with app.test_client() as client:
            resp = client.post(
                '/posts/a/edit', data={'title': 'Something Different', 'content': 'Almost not repetitive!'})

            self.assertEqual(resp.status_code, 404)

    def test_delete_post(self):
        with app.test_client() as client:
            resp = client.post('/posts/1/delete')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/users/1')

            resp2 = client.get('/users/1')
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h1>John Doe</h1>', html)
            self.assertNotIn('<li><a href="/posts/1">A Test</a></li>', html)
            self.assertNotIn('WARNINGS GO HERE', html)

    def test_delete_non_post(self):
        with app.test_client() as client:
            resp = client.post('/posts/2/delete')

            self.assertEqual(resp.status_code, 404)

    def test_delete_non_post2(self):
        with app.test_client() as client:
            resp = client.post('/posts/a/delete')

            self.assertEqual(resp.status_code, 404)
