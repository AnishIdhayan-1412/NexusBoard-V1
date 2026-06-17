import logging
from django.db import models
from django.db.models import F
from django.urls import reverse
from django.conf import settings

logger = logging.getLogger('canopy')


class Post(models.Model):
    POST_TYPES = [
        ('text', 'Text'),
        ('link', 'Link'),
        ('image', 'Image'),
    ]
    title = models.CharField(max_length=300, db_index=True)
    body = models.TextField(blank=True)
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text', db_index=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    community = models.ForeignKey(
        'communities.Community',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False, db_index=True)
    is_locked = models.BooleanField(default=False)
    upvotes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Vote',
        related_name='voted_posts'
    )
    # Cached counters — updated atomically on vote/comment actions
    score = models.IntegerField(default=0, db_index=True)
    comment_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['community', '-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['-score', '-created_at']),
        ]

    def get_absolute_url(self):
        return reverse('posts:detail', kwargs={'pk': self.pk})

    @property
    def vote_score(self):
        """Use cached score field; falls back to DB count if needed."""
        return self.score

    @property
    def total_comment_count(self):
        return self.comments.count()

    def update_score(self):
        """Recalculate and persist score atomically."""
        from django.db.models import Sum, Case, When, IntegerField
        result = self.vote_set.aggregate(
            total=Sum(
                Case(
                    When(value=1, then=1),
                    When(value=-1, then=-1),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )['total'] or 0
        Post.objects.filter(pk=self.pk).update(score=result)
        self.score = result

    def __str__(self):
        return self.title


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, 'Up'), (-1, 'Down')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['post', 'value']),
        ]

    def __str__(self):
        return f"{self.user} {'↑' if self.value == 1 else '↓'} {self.post}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments'
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies'
    )
    body = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    # Cached vote score
    score = models.IntegerField(default=0)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'parent', 'created_at']),
        ]

    @property
    def vote_score(self):
        return self.score

    def update_score(self):
        from django.db.models import Sum, Case, When, IntegerField
        result = self.comment_votes.aggregate(
            total=Sum(
                Case(
                    When(value=1, then=1),
                    When(value=-1, then=-1),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )['total'] or 0
        Comment.objects.filter(pk=self.pk).update(score=result)
        self.score = result

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"


class CommentVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_votes')
    value = models.SmallIntegerField(choices=[(1, 'Up'), (-1, 'Down')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f"{self.user} {'↑' if self.value == 1 else '↓'} comment"
