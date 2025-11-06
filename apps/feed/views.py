from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json

from apps.accounts.models import User
from apps.core.utils import paginate_queryset
from apps.feed.models import Post, Comment, Reaction, Bookmark, Follow


def index(request):
    posts = Post.objects.all().order_by("-created_date")
    page_obj = paginate_queryset(request, posts)
    return render(request, "feed/index.html", {"posts_page": page_obj})


@login_required
def following(request):
    followed_users = Follow.objects.following(request.user).values_list(
        "followed", flat=True
    )
    posts = (
        Post.objects.all().filter(author__in=followed_users).order_by("-created_date")
    )
    page_obj = paginate_queryset(request, posts)
    return render(request, "feed/following.html", {"posts_page": page_obj})


def post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.for_post(post)
    return render(request, "feed/post.html", {"post": post, "comments": comments})


@login_required
def new_post(request):
    if request.method == "GET":
        return render(request, "feed/new_post.html")

    body = request.POST.get("body", "").strip()
    if body:
        post = Post.objects.create(author=request.user, body=body)
        return redirect("feed:post", post_id=post.id)
    return redirect("feed:index")


@login_required
@require_POST
@csrf_exempt
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    data = json.loads(request.body)
    post.body = data.get("body", "")
    post.save()
    return JsonResponse({"status": "201", "postContent": post.body})


@login_required
@require_POST
@csrf_exempt
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    post.delete()
    return JsonResponse({"status": "201", "action": f"Deleted post: {post_id}"})


@login_required
@require_POST
def comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    body = request.POST.get("body", "").strip()
    if body:
        Comment.objects.create(post=post, author=request.user, body=body)
    return redirect("feed:post", post_id=post_id)


@login_required
@require_POST
@csrf_exempt
def connect(request, username):
    """
    Follow or unfollow a user.
    """
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        messages.warning(request, "You cannot follow yourself.")
        return JsonResponse(
            {"status": "400", "response": "You cannot follow yourself."}
        )

    follow, created = Follow.objects.follow(follower=request.user, followed=target_user)

    if not created:
        Follow.objects.unfollow(follower=request.user, followed=target_user)
        messages.info(request, f"You have unfollowed @{username}.")
        return JsonResponse({"status": "201", "response": "Unfollowed"})

    messages.success(request, f"You are now following @{username}.")
    return JsonResponse({"status": "201", "response": "Followed"})


@login_required
@require_POST
@csrf_exempt
def react(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if Reaction.objects.has_liked(user=request.user, post=post):
        Reaction.objects.unlike(user=request.user, post=post)
        action = "Unliked"
    else:
        Reaction.objects.like(user=request.user, post=post)
        action = "Liked"

    return JsonResponse(
        {
            "status": "201",
            "action": action,
            "postReactionsCount": Reaction.objects.for_post(post).count(),
        }
    )


@login_required
def bookmarks(request):
    bookmarks = (
        Bookmark.objects.filter(user=request.user)
        .select_related("post")
        .order_by("-created_date")
    )

    bookmarked_posts = [bookmark.post for bookmark in bookmarks if bookmark.post]
    page_obj = paginate_queryset(request, bookmarked_posts)

    return render(request, "feed/bookmarks.html", {"posts_page": page_obj})


@login_required
@require_POST
@csrf_exempt
def bookmark(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if Bookmark.objects.has_bookmarked(request.user, post):
        Bookmark.objects.remove_bookmark(request.user, post)
        action = "Bookmark Removed"
    else:
        Bookmark.objects.add_bookmark(request.user, post)
        action = "Bookmarked"

    return JsonResponse({"status": "201", "action": action})


@login_required
@require_POST
@csrf_exempt
def pin_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, author=request.user)

    if post.is_pinned:
        post.is_pinned = False
    else:
        Post.objects.filter(author=request.user, is_pinned=True).update(is_pinned=False)
        post.is_pinned = True

    post.save()
    return JsonResponse(
        {
            "status": "201",
            "post": f"Pinned post: {post_id}",
            "username": post.author.username,
        }
    )
