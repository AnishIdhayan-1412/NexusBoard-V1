from django.contrib import admin
from .models import Post, Comment, Vote, CommentVote


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'community', 'post_type', 'vote_score', 'created_at']
    list_filter = ['post_type', 'is_pinned', 'is_locked', 'created_at']
    search_fields = ['title', 'body']
    raw_id_fields = ['author', 'community']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at', 'is_deleted']
    list_filter = ['is_deleted', 'created_at']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'value', 'created_at']
