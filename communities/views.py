import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from .models import Community, Membership
from .forms import CommunityCreateForm

logger = logging.getLogger('nexusboard')


def community_list_view(request):
    communities = Community.objects.all().order_by('-created_at')
    return render(request, 'communities/list.html', {'communities': communities})


def community_detail_view(request, slug):
    community = get_object_or_404(Community, slug=slug)
    posts = community.posts.select_related('author').order_by('-created_at')[:20]
    is_member = False
    user_role = None
    if request.user.is_authenticated:
        membership = Membership.objects.filter(user=request.user, community=community, is_active=True).first()
        if membership:
            is_member = True
            user_role = membership.role
    context = {
        'community': community,
        'posts': posts,
        'is_member': is_member,
        'user_role': user_role,
    }
    return render(request, 'communities/detail.html', context)


@login_required
def community_create_view(request):
    if request.method == 'POST':
        form = CommunityCreateForm(request.POST, request.FILES)
        if form.is_valid():
            community = form.save(commit=False)
            community.created_by = request.user
            community.slug = slugify(community.name)
            community.save()
            Membership.objects.create(user=request.user, community=community, role='admin')
            logger.info(f"Community created: {community.name} by {request.user.username}")
            messages.success(request, f"Community c/{community.name} created!")
            return redirect('communities:detail', slug=community.slug)
    else:
        form = CommunityCreateForm()
    return render(request, 'communities/create.html', {'form': form})


@login_required
@require_POST
def join_community_view(request, slug):
    community = get_object_or_404(Community, slug=slug)
    membership, created = Membership.objects.get_or_create(
        user=request.user, community=community,
        defaults={'is_active': True}
    )
    if not created:
        membership.is_active = not membership.is_active
        membership.save()
        action = 'joined' if membership.is_active else 'left'
    else:
        action = 'joined'
    messages.success(request, f"You have {action} c/{community.name}")
    return redirect('communities:detail', slug=community.slug)
