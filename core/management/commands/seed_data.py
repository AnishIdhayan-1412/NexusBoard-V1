"""
Seed command: python manage.py seed_data
Creates sample communities, posts, and a superuser for quick dev testing.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from communities.models import Community, Membership
from posts.models import Post, Comment
from django.utils.text import slugify

User = get_user_model()

COMMUNITIES = [
    ('Technology', 'tech', 'All things tech: programming, gadgets, AI, and more.'),
    ('ScienceHub', 'science', 'Explore the universe through science, research, and discovery.'),
    ('Startups', 'startups', 'Entrepreneurship, funding, product launches, and startup culture.'),
    ('DevOps', 'devops', 'Docker, Kubernetes, CI/CD, cloud infrastructure, and SRE practices.'),
    ('Python', 'python', 'The Python programming language, libraries, and ecosystem.'),
]

POSTS = [
    ('Technology', 'I just deployed my first app to production!', 'After 3 months of learning Django and DevOps, my app is live. AMA!'),
    ('Technology', 'Best free tools for developers in 2025', 'Sharing my toolkit: VS Code, Docker Desktop, Postman, and more...'),
    ('DevOps', 'Docker Compose vs Kubernetes: When to use what?', 'For most small projects, Docker Compose is more than enough. Kubernetes shines when you need orchestration at scale.'),
    ('Python', 'Django vs FastAPI for a social platform', 'Django wins on batteries-included: auth, admin, ORM, templates. FastAPI is faster but you build more yourself.'),
    ('Startups', 'Launched on Product Hunt today — lessons learned', 'We got 400 upvotes but here is what I wish I knew before launching...'),
    ('ScienceHub', 'New study on AI and creative problem solving', 'Researchers found that AI augmentation improves human creative output by ~30% in structured tasks.'),
]

class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding database...')

        # Create admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@nexusboard.com', 'adminpass123')
            admin.bio = 'NexusBoard administrator'
            admin.save()
            self.stdout.write('✅ Admin user created (admin/adminpass123)')

        # Create test users
        users = []
        for i in range(1, 4):
            username = f'user{i}'
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username, f'{username}@example.com', 'testpass123')
                u.bio = f'I am {username}, a NexusBoard member!'
                u.save()
                users.append(u)
                self.stdout.write(f'✅ Created {username}')
            else:
                users.append(User.objects.get(username=username))

        admin_user = User.objects.get(username='admin')

        # Create communities
        for name, slug_hint, desc in COMMUNITIES:
            slug = slugify(name)
            if not Community.objects.filter(slug=slug).exists():
                community = Community.objects.create(
                    name=name, slug=slug, description=desc, created_by=admin_user
                )
                Membership.objects.create(user=admin_user, community=community, role='admin')
                for u in users:
                    Membership.objects.create(user=u, community=community, role='member')
                self.stdout.write(f'✅ Community: c/{name}')

        # Create posts
        for comm_name, title, body in POSTS:
            if not Post.objects.filter(title=title).exists():
                community = Community.objects.get(name=comm_name)
                post = Post.objects.create(
                    title=title, body=body,
                    author=admin_user, community=community,
                    post_type='text'
                )
                # Add a comment
                Comment.objects.create(
                    post=post, author=users[0],
                    body='Great post! Thanks for sharing.'
                )
                self.stdout.write(f'✅ Post: {title[:40]}...')

        self.stdout.write('\n🎉 Database seeded! You can now log in at /admin with admin/adminpass123')
        self.stdout.write('   Or visit the site and log in with user1/testpass123')
