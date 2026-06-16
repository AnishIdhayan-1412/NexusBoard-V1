import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import User, Follow
from .forms import RegisterForm, LoginForm, ProfileEditForm
from django_ratelimit.decorators import ratelimit

logger = logging.getLogger('canopy')

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f"New user registered: {user.username}")
            messages.success(request, f"Welcome to Canopy, {user.username}! 🎉")
            return redirect('core:home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"User logged in: {user.username}")
            # Security: validate next is a safe local URL to prevent open redirect.
            # An attacker could craft ?next=https://evil.com to redirect after login.
            from django.utils.http import url_has_allowed_host_and_scheme
            next_url = request.GET.get('next', '')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('core:home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    if request.method == 'POST':
        logger.info(f"User logged out: {request.user.username}")
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.select_related('community').order_by('-created_at')[:20]
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
        'post_count': profile_user.posts.count(),
        'comment_count': profile_user.comments.count(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
@require_POST
def follow_toggle_view(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    follow_obj, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target_user
    )
    if not created:
        follow_obj.delete()
        following = False
    else:
        following = True
    return JsonResponse({
        'following': following,
        'follower_count': target_user.follower_count
    })
