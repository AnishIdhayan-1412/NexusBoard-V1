import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from posts.models import Post
from communities.models import Community, Membership
from accounts.models import User

logger = logging.getLogger('canopy')

PAGE_SIZE = 20


def home_view(request):
    if request.user.is_authenticated:
        joined_ids = request.user.joined_communities.filter(
            membership__is_active=True
        ).values_list('id', flat=True)
        if joined_ids:
            qs = Post.objects.filter(
                community_id__in=joined_ids
            ).select_related('author', 'community').order_by('-is_pinned', '-created_at')
        else:
            qs = Post.objects.select_related(
                'author', 'community'
            ).order_by('-score', '-created_at')
    else:
        qs = Post.objects.select_related(
            'author', 'community'
        ).order_by('-score', '-created_at')

    paginator = Paginator(qs, PAGE_SIZE)
    page = paginator.get_page(request.GET.get('page'))

    trending = Community.objects.order_by('-post_count')[:8]

    return render(request, 'core/home.html', {
        'page_obj': page,
        'trending_communities': trending,
    })


def about_view(request):
    return render(request, 'core/about.html')


def search_view(request):
    query = request.GET.get('q', '').strip()
    post_page = community_page = user_page = None

    if query:
        post_qs = Post.objects.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        ).select_related('author', 'community').order_by('-score')

        comm_qs = Community.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by('-member_count')

        user_qs = User.objects.filter(
            Q(username__icontains=query) | Q(bio__icontains=query)
        ).order_by('-reputation')

        post_page = Paginator(post_qs, PAGE_SIZE).get_page(request.GET.get('page'))
        community_page = Paginator(comm_qs, 10).get_page(1)
        user_page = Paginator(user_qs, 10).get_page(1)

    return render(request, 'core/search.html', {
        'query': query,
        'post_page': post_page,
        'community_page': community_page,
        'user_page': user_page,
    })


def health_check_view(request):
    from django.db import connection
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False
    status = 'healthy' if db_ok else 'degraded'
    code = 200 if db_ok else 503
    return JsonResponse({'status': status, 'app': 'Canopy', 'db': db_ok}, status=code)
