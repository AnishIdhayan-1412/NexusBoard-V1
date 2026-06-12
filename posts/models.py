from django.db import models
from django.urls import reverse
from django.conf import settings


class Post(models.Model):
    POST_TYPES = [
        ('text', 'Text'),
        ('link', 'Link'),
        ('image', 'Image'),
    ]
    title = models.CharField(max_length=300)
    body = models.TextField(blank=True)
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    upvotes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Vote',
        related_name='voted_posts'
    )

    class Meta:
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('posts:detail', kwargs={'pk': self.pk})

    @property
    def vote_score(self):
        ups = self.vote_set.filter(value=1).count()
        downs = self.vote_set.filter(value=-1).count()
        return ups - downs

    @property
    def comment_count(self):
        return self.comments.filter(parent=None).count()

    @property
    def total_comment_count(self):
        return self.comments.count()

    def __str__(self):
        return self.title


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, 'Up'), (-1, 'Down')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user} {'↑' if self.value == 1 else '↓'} {self.post}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    body = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    @property
    def vote_score(self):
        ups = self.comment_votes.filter(value=1).count()
        downs = self.comment_votes.filter(value=-1).count()
        return ups - downs

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
