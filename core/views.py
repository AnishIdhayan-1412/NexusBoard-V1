import logging
from django.shortcuts import render
from django.db.models import Count
from posts.models import Post
from communities.models import Community

logger = logging.getLogger('nexusboard')


def home_view(request):
    if request.user.is_authenticated:
        joined_ids = request.user.joined_communities.values_list('id', flat=True)
        if joined_ids:
            posts = Post.objects.filter(community_id__in=joined_ids).select_related('author', 'community').order_by('-created_at')[:25]
        else:
            posts = Post.objects.select_related('author', 'community').order_by('-created_at')[:25]
    else:
        posts = Post.objects.select_related('author', 'community').order_by('-created_at')[:25]

    trending_communities = Community.objects.annotate(
        num_posts=Count('posts')
    ).order_by('-num_posts')[:8]

    context = {
        'posts': posts,
        'trending_communities': trending_communities,
    }
    return render(request, 'core/home.html', context)


def about_view(request):
    return render(request, 'core/about.html')


def search_view(request):
    query = request.GET.get('q', '').strip()
    posts = []
    communities = []
    if query:
        posts = Post.objects.filter(title__icontains=query).select_related('author', 'community')[:20]
        communities = Community.objects.filter(name__icontains=query)[:10]
    return render(request, 'core/search.html', {
        'query': query,
        'posts': posts,
        'communities': communities,
    })


def health_check_view(request):
    from django.http import JsonResponse
    return JsonResponse({
        'status': 'healthy',
        'app': 'NexusBoard'
    })