from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from communities.models import Community, Membership


def make_user(username='u', password='TestPass123!'):
    return User.objects.create_user(username=username, password=password)


class SlugTest(TestCase):
    def test_slug_auto_generated(self):
        u = make_user()
        c = Community.objects.create(name='My Community', description='d', created_by=u)
        self.assertEqual(c.slug, 'my-community')

    def test_slug_collision_gets_suffix(self):
        """Two different names that slugify identically get unique slugs."""
        u = make_user()
        c1 = Community.objects.create(name='Tech-Talk', description='d', created_by=u)
        # Simulate slug collision by manually setting slug then creating another
        c2 = Community(name='Tech Info', description='d2', created_by=u)
        c2.slug = c1.slug  # force collision
        c2.slug = c2._unique_slug()
        c2.save()
        self.assertNotEqual(c1.slug, c2.slug)

    def test_no_slug_provided_creates_from_name(self):
        u = make_user()
        c = Community.objects.create(name='Hello World', description='d', created_by=u)
        self.assertTrue(c.slug.startswith('hello'))


class MemberCountTest(TestCase):
    def test_join_updates_member_count(self):
        u = make_user()
        u2 = make_user('u2')
        c = Community.objects.create(name='Jointest', description='d', created_by=u)
        Membership.objects.create(user=u, community=c, role='admin')
        c.recalc_member_count()
        self.assertEqual(c.member_count, 1)
        client = Client()
        client.login(username='u2', password='TestPass123!')
        client.post(reverse('communities:join', kwargs={'slug': c.slug}))
        c.refresh_from_db()
        self.assertEqual(c.member_count, 2)
