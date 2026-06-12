from django.db import models
from django.urls import reverse
from django.conf import settings


class Community(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=1000)
    banner = models.ImageField(upload_to='community_banners/', blank=True, null=True)
    icon = models.ImageField(upload_to='community_icons/', blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_communities'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=False)
    rules = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Communities'
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('communities:detail', kwargs={'slug': self.slug})

    @property
    def member_count(self):
        return self.membership_set.filter(is_active=True).count()

    @property
    def post_count(self):
        return self.posts.count()

    def __str__(self):
        return f"c/{self.name}"


class Membership(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'community')
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user} in {self.community} ({self.role})"
