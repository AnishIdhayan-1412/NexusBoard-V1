import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count
from .models import Post, Comment, Vote, CommentVote
from .forms import PostCreateForm, CommentForm
from communities.models import Community

logger = logging.getLogger('nexusboard')


def post_list_view(request):
    posts = Post.objects.select_related('author', 'community').order_by('-created_at')[:30]
    return render(request, 'posts/list.html', {'posts': posts})


def post_detail_view(request, pk):
    post = get_object_or_404(Post.objects.select_related('author', 'community'), pk=pk)
    comments = post.comments.filter(parent=None).select_related('author').prefetch_related(
        'replies__author'
    )
    comment_form = CommentForm()
    user_vote = None
    if request.user.is_authenticated:
        vote = Vote.objects.filter(user=request.user, post=post).first()
        user_vote = vote.value if vote else None
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'user_vote': user_vote,
    }
    return render(request, 'posts/detail.html', context)


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
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            logger.info(f"Post created: {post.pk} by {request.user.username}")
            messages.success(request, 'Post submitted successfully!')
            return redirect('posts:detail', pk=post.pk)
    else:
        form = PostCreateForm(user=request.user, initial=initial)
    communities = Community.objects.all()
    return render(request, 'posts/create.html', {'form': form, 'communities': communities})


@login_required
def add_comment_view(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, pk=parent_id)
            comment.save()
            messages.success(request, 'Comment added!')
    return redirect('posts:detail', pk=post_pk)


@login_required
def vote_post_view(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    post = get_object_or_404(Post, pk=pk)
    try:
        value = int(request.POST.get('value', 1))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid value'}, status=400)
    if value not in [1, -1]:
        return JsonResponse({'error': 'Invalid value'}, status=400)

    vote, created = Vote.objects.get_or_create(user=request.user, post=post, defaults={'value': value})
    if not created:
        if vote.value == value:
            vote.delete()
            user_vote = None
        else:
            vote.value = value
            vote.save()
            user_vote = value
    else:
        user_vote = value

    return JsonResponse({'score': post.vote_score, 'user_vote': user_vote})


@login_required
def delete_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'Permission denied.')
        return redirect('posts:detail', pk=pk)
    if request.method == 'POST':
        community_slug = post.community.slug
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('communities:detail', slug=community_slug)
    return render(request, 'posts/confirm_delete.html', {'post': post})
