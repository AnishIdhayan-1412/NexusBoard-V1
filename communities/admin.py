from django.contrib import admin
from .models import Community, Membership


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'is_private', 'member_count', 'post_count', 'created_at']
    list_filter = ['is_private', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'community', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active']
