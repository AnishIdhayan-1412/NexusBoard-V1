from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from communities.models import Community, Membership
from posts.models import Post, Comment, Vote

User = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpass123')

    def test_register_page_loads(self):
        r = self.client.get(reverse('accounts:register'))
        self.assertEqual(r.status_code, 200)

    def test_login_page_loads(self):
        r = self.client.get(reverse('accounts:login'))
        self.assertEqual(r.status_code, 200)

    def test_register_creates_user(self):
        r = self.client.post(reverse('accounts:register'), {
            'username': 'newuser', 'email': 'new@test.com',
            'password1': 'ComplexPass1!', 'password2': 'ComplexPass1!'
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_works(self):
        r = self.client.post(reverse('accounts:login'), {
            'username': 'testuser', 'password': 'testpass123'
        })
        self.assertEqual(r.status_code, 302)

    def test_profile_page_loads(self):
        r = self.client.get(reverse('accounts:profile', kwargs={'username': 'testuser'}))
        self.assertEqual(r.status_code, 200)


class CommunityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpass123')
        self.community = Community.objects.create(
            name='TestComm', slug='testcomm',
            description='A test community', created_by=self.user
        )
        Membership.objects.create(user=self.user, community=self.community, role='admin')

    def test_community_list_loads(self):
        r = self.client.get(reverse('communities:list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'TestComm')

    def test_community_detail_loads(self):
        r = self.client.get(reverse('communities:detail', kwargs={'slug': 'testcomm'}))
        self.assertEqual(r.status_code, 200)

    def test_create_community_requires_login(self):
        r = self.client.get(reverse('communities:create'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/accounts/login/', r['Location'])

    def test_create_community_works(self):
        self.client.login(username='testuser', password='testpass123')
        r = self.client.post(reverse('communities:create'), {
            'name': 'NewCommunity', 'description': 'A new one',
            'is_private': False, 'rules': ''
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Community.objects.filter(name='NewCommunity').exists())


class PostTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpass123')
        self.community = Community.objects.create(
            name='TestComm', slug='testcomm',
            description='Test', created_by=self.user
        )
        Membership.objects.create(user=self.user, community=self.community, role='admin')
        self.post = Post.objects.create(
            title='Test Post', body='Test body',
            author=self.user, community=self.community, post_type='text'
        )

    def test_post_detail_loads(self):
        r = self.client.get(reverse('posts:detail', kwargs={'pk': self.post.pk}))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Test Post')

    def test_create_post_requires_login(self):
        r = self.client.get(reverse('posts:create'))
        self.assertEqual(r.status_code, 302)

    def test_create_post_works(self):
        self.client.login(username='testuser', password='testpass123')
        r = self.client.post(reverse('posts:create'), {
            'title': 'My New Post', 'body': 'Hello world',
            'post_type': 'text', 'community': self.community.pk
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Post.objects.filter(title='My New Post').exists())

    def test_vote_post_ajax(self):
        self.client.login(username='testuser', password='testpass123')
        r = self.client.post(
            reverse('posts:vote', kwargs={'pk': self.post.pk}),
            {'value': 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn('score', r.json())

    def test_add_comment(self):
        self.client.login(username='testuser', password='testpass123')
        r = self.client.post(reverse('posts:add_comment', kwargs={'post_pk': self.post.pk}), {
            'body': 'This is a comment'
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Comment.objects.filter(post=self.post).exists())

    def test_vote_score_calculation(self):
        user2 = User.objects.create_user('user2', 'u2@test.com', 'testpass123')
        Vote.objects.create(user=self.user, post=self.post, value=1)
        Vote.objects.create(user=user2, post=self.post, value=1)
        self.assertEqual(self.post.vote_score, 2)


class HomeAndSearchTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpass123')
        self.community = Community.objects.create(
            name='Tech', slug='tech', description='Tech stuff', created_by=self.user
        )
        Membership.objects.create(user=self.user, community=self.community, role='admin')
        Post.objects.create(
            title='Unique Searchable Title XYZ123',
            body='Body text', author=self.user,
            community=self.community, post_type='text'
        )

    def test_home_loads(self):
        r = self.client.get(reverse('core:home'))
        self.assertEqual(r.status_code, 200)

    def test_search_finds_post(self):
        r = self.client.get(reverse('core:search'), {'q': 'XYZ123'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Unique Searchable Title XYZ123')

    def test_health_check(self):
        r = self.client.get(reverse('core:health'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['status'], 'healthy')
