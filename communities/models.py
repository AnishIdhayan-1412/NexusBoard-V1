from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify


class Community(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True)
    description = models.TextField(max_length=1000)
    banner = models.ImageField(upload_to='community_banners/', blank=True, null=True)
    icon = models.ImageField(upload_to='community_icons/', blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_communities'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=False)
    rules = models.TextField(blank=True)
    # Cached counters
    member_count = models.PositiveIntegerField(default=0)
    post_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Communities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-member_count']),
            models.Index(fields=['-post_count']),
        ]

    def get_absolute_url(self):
        return reverse('communities:detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._unique_slug()
        super().save(*args, **kwargs)

    def _unique_slug(self):
        base = slugify(self.name)
        slug = base
        counter = 1
        while Community.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{counter}"
            counter += 1
        return slug

    def recalc_member_count(self):
        count = self.membership_set.filter(is_active=True).count()
        Community.objects.filter(pk=self.pk).update(member_count=count)
        self.member_count = count

    def recalc_post_count(self):
        count = self.posts.count()
        Community.objects.filter(pk=self.pk).update(post_count=count)
        self.post_count = count

    def __str__(self):
        return self.name


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
        indexes = [
            models.Index(fields=['community', 'is_active', 'role']),
        ]

    def __str__(self):
        return f"{self.user} in {self.community} ({self.role})"
