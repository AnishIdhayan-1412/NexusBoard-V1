from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from communities.models import Community, Membership
from posts.models import Post, Vote, Comment


def make_user(username='testuser', password='TestPass123!'):
    return User.objects.create_user(username=username, password=password)


def make_community(user, name='TestComm'):
    c = Community.objects.create(
        name=name, description='Test', created_by=user
    )
    Membership.objects.create(user=user, community=c, role='admin')
    return c


def make_post(author, community, title='Test Post'):
    return Post.objects.create(
        title=title, body='body', post_type='text',
        author=author, community=community
    )


class VoteTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.other = make_user('other')
        self.comm = make_community(self.user)
        self.post = make_post(self.other, self.comm)
        self.client = Client()
        self.client.login(username='testuser', password='TestPass123!')

    def test_upvote_creates_vote_and_updates_score(self):
        url = reverse('posts:vote', kwargs={'pk': self.post.pk})
        resp = self.client.post(url, {'value': '1'})
        self.assertEqual(resp.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.score, 1)

    def test_double_vote_cancels(self):
        url = reverse('posts:vote', kwargs={'pk': self.post.pk})
        self.client.post(url, {'value': '1'})
        self.client.post(url, {'value': '1'})  # cancel
        self.post.refresh_from_db()
        self.assertEqual(self.post.score, 0)

    def test_vote_requires_login(self):
        c = Client()
        url = reverse('posts:vote', kwargs={'pk': self.post.pk})
        resp = c.post(url, {'value': '1'})
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp['Location'])

    def test_invalid_vote_value_rejected(self):
        url = reverse('posts:vote', kwargs={'pk': self.post.pk})
        resp = self.client.post(url, {'value': '99'})
        self.assertEqual(resp.status_code, 400)

    def test_vote_updates_author_reputation(self):
        url = reverse('posts:vote', kwargs={'pk': self.post.pk})
        self.client.post(url, {'value': '1'})
        self.other.refresh_from_db()
        self.assertEqual(self.other.reputation, 1)


class DeletePermissionTests(TestCase):
    def setUp(self):
        self.author = make_user('author')
        self.mod = make_user('mod')
        self.rando = make_user('rando')
        self.comm = make_community(self.author)
        Membership.objects.create(user=self.mod, community=self.comm, role='moderator')
        self.post = make_post(self.author, self.comm)

    def _delete(self, user):
        c = Client()
        c.login(username=user.username, password='TestPass123!')
        return c.post(reverse('posts:delete', kwargs={'pk': self.post.pk}))

    def test_author_can_delete(self):
        resp = self._delete(self.author)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_moderator_can_delete(self):
        resp = self._delete(self.mod)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_random_user_cannot_delete(self):
        resp = self._delete(self.rando)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())


class CommentTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.comm = make_community(self.user)
        self.post = make_post(self.user, self.comm)
        self.client = Client()
        self.client.login(username='testuser', password='TestPass123!')

    def test_add_comment_increments_count(self):
        url = reverse('posts:add_comment', kwargs={'post_pk': self.post.pk})
        self.client.post(url, {'body': 'hello world'})
        self.post.refresh_from_db()
        self.assertEqual(self.post.comment_count, 1)

    def test_locked_post_rejects_comment(self):
        self.post.is_locked = True
        self.post.save()
        url = reverse('posts:add_comment', kwargs={'post_pk': self.post.pk})
        self.client.post(url, {'body': 'should fail'})
        self.assertEqual(self.post.comments.count(), 0)
