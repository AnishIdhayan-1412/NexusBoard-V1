from django.contrib import admin
from .models import Post, Vote, Comment, CommentVote


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'community', 'post_type', 'score', 'comment_count', 'is_pinned', 'is_locked', 'created_at')
    list_filter = ('post_type', 'is_pinned', 'is_locked', 'community')
    search_fields = ('title', 'body', 'author__username')
    raw_id_fields = ('author', 'community')
    readonly_fields = ('score', 'comment_count', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    actions = ['pin_posts', 'unpin_posts', 'lock_posts', 'unlock_posts']

    def pin_posts(self, request, qs):
        qs.update(is_pinned=True)
    pin_posts.short_description = 'Pin selected posts'

    def unpin_posts(self, request, qs):
        qs.update(is_pinned=False)
    unpin_posts.short_description = 'Unpin selected posts'

    def lock_posts(self, request, qs):
        qs.update(is_locked=True)
    lock_posts.short_description = 'Lock selected posts'

    def unlock_posts(self, request, qs):
        qs.update(is_locked=False)
    unlock_posts.short_description = 'Unlock selected posts'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'score', 'is_deleted', 'created_at')
    list_filter = ('is_deleted',)
    search_fields = ('body', 'author__username')
    raw_id_fields = ('author', 'post', 'parent')
    readonly_fields = ('score', 'created_at', 'updated_at')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'value', 'created_at')
    raw_id_fields = ('user', 'post')


@admin.register(CommentVote)
class CommentVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'value', 'created_at')
    raw_id_fields = ('user', 'comment')
