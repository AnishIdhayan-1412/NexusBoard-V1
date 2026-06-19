import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db import models, transaction
from .models import Post, Comment, Vote, CommentVote
from .forms import PostCreateForm, CommentForm
from communities.models import Community, Membership

logger = logging.getLogger('canopy')

PAGE_SIZE = 20


def post_list_view(request):
    sort = request.GET.get('sort', 'new')
    if sort == 'top':
        order = ['-score', '-created_at']
    elif sort == 'hot':
        order = ['-is_pinned', '-score', '-created_at']
    else:
        order = ['-created_at']
    qs = Post.objects.select_related('author', 'community').order_by(*order)
    paginator = Paginator(qs, PAGE_SIZE)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'posts/list.html', {'page_obj': page, 'current_sort': sort})


def post_detail_view(request, pk):
    post = get_object_or_404(
        Post.objects.select_related('author', 'community'), pk=pk
    )
    comments = post.comments.filter(
        parent=None, is_deleted=False
    ).select_related('author').prefetch_related(
        'replies__author'
    )
    comment_form = CommentForm()
    user_vote = None
    if request.user.is_authenticated:
        vote = Vote.objects.filter(user=request.user, post=post).first()
        user_vote = vote.value if vote else None
    return render(request, 'posts/detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'user_vote': user_vote,
    })


@login_required
def post_create_view(request):
    community_slug = request.GET.get('community')
    initial = {}
    if community_slug:
        community = Community.objects.filter(slug=community_slug).first()
        if community:
            initial['community'] = community

    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                # Update community post count
                post.community.recalc_post_count()
            logger.info("Post created: %s by %s", post.pk, request.user.username)
            messages.success(request, 'Post submitted successfully!')
            return redirect('posts:detail', pk=post.pk)
    else:
        form = PostCreateForm(user=request.user, initial=initial)
    return render(request, 'posts/create.html', {
        'form': form,
        'communities': Community.objects.order_by('name')[:200],
    })


@login_required
@require_POST
def add_comment_view(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if post.is_locked:
        messages.error(request, 'This post is locked.')
        return redirect('posts:detail', pk=post_pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        with transaction.atomic():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, pk=parent_id)
            comment.save()
            # Atomically increment cached comment_count.
            # Using F() avoids a race condition where .count() could read
            # stale data when two comments are saved concurrently.
            Post.objects.filter(pk=post.pk).update(
                comment_count=models.F('comment_count') + 1
            )
            # Reputation: +1 to post author for receiving a comment
            if comment.author != post.author:
                post.author.adjust_reputation(1)
        messages.success(request, 'Comment added!')
    return redirect('posts:detail', pk=post_pk)


@login_required
@require_POST
def vote_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    try:
        value = int(request.POST.get('value', 1))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid value'}, status=400)
    if value not in [1, -1]:
        return JsonResponse({'error': 'Invalid value'}, status=400)

    with transaction.atomic():
        vote, created = Vote.objects.get_or_create(
            user=request.user, post=post, defaults={'value': value}
        )
        if not created:
            old_value = vote.value
            if vote.value == value:
                vote.delete()
                user_vote = None
                # Undo reputation
                if request.user != post.author:
                    post.author.adjust_reputation(-value)
            else:
                vote.value = value
                vote.save()
                user_vote = value
                # Reputation swing: e.g. from -1 to +1 = +2
                if request.user != post.author:
                    post.author.adjust_reputation(value - old_value)
        else:
            user_vote = value
            if request.user != post.author:
                post.author.adjust_reputation(value)
        post.update_score()

    return JsonResponse({'score': post.score, 'user_vote': user_vote})


@login_required
def delete_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # Allow: post author, community moderator/admin, or site staff
    is_mod = Membership.objects.filter(
        user=request.user,
        community=post.community,
        role__in=['moderator', 'admin'],
        is_active=True
    ).exists()
    if not (post.author == request.user or is_mod or request.user.is_staff):
        messages.error(request, 'Permission denied.')
        return redirect('posts:detail', pk=pk)
    if request.method == 'POST':
        community_slug = post.community.slug
        with transaction.atomic():
            post.delete()
            post.community.recalc_post_count()
        messages.success(request, 'Post deleted.')
        return redirect('communities:detail', slug=community_slug)
    return render(request, 'posts/confirm_delete.html', {'post': post})


@login_required
@require_POST
def vote_comment_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    try:
        value = int(request.POST.get('value', 1))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid value'}, status=400)
    if value not in [1, -1]:
        return JsonResponse({'error': 'Invalid value'}, status=400)

    with transaction.atomic():
        vote, created = CommentVote.objects.get_or_create(
            user=request.user, comment=comment, defaults={'value': value}
        )
        if not created:
            old_value = vote.value
            if vote.value == value:
                vote.delete()
                user_vote = None
                if request.user != comment.author:
                    comment.author.adjust_reputation(-value)
            else:
                vote.value = value
                vote.save()
                user_vote = value
                if request.user != comment.author:
                    comment.author.adjust_reputation(value - old_value)
        else:
            user_vote = value
            if request.user != comment.author:
                comment.author.adjust_reputation(value)
        comment.update_score()

    return JsonResponse({'score': comment.score, 'user_vote': user_vote})
