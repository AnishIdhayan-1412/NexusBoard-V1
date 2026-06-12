from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    reputation = models.IntegerField(default=0, db_index=True)
    joined_communities = models.ManyToManyField(
        'communities.Community',
        through='communities.Membership',
        related_name='members'
    )
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        through='Follow',
        related_name='following'
    )

    class Meta:
        verbose_name = 'User'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['-reputation']),
        ]

    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.username})

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return f"https://ui-avatars.com/api/?name={self.username}&background=6366f1&color=fff&size=128"

    @property
    def follower_count(self):
        return self.followed_by_set.count()

    @property
    def following_count(self):
        return self.follow_set.count()

    def adjust_reputation(self, delta: int):
        """Atomically adjust reputation — never call user.reputation += delta."""
        User.objects.filter(pk=self.pk).update(reputation=models.F('reputation') + delta)
        self.reputation += delta

    def __str__(self):
        return self.username


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_by_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower} → {self.following}"
