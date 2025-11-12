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
    posts = Post.objects.with_full_details(user=request.user).order_by("-created_date")
    page_obj = paginate_queryset(request, posts)
    return render(request, "feed/index.html", {"posts_page": page_obj})


def post(request, post_id):
    current_user = request.user if request.user.is_authenticated else None
    post = get_object_or_404(Post.objects.with_full_details(current_user), pk=post_id)
    comments = Comment.objects.for_post(post)
    return render(request, "feed/post.html", {"post": post, "comments": comments})


@login_required
def following(request):
    posts = Post.objects.feed_for_user(request.user)
    page_obj = paginate_queryset(request, posts)
    return render(request, "feed/following.html", {"posts_page": page_obj})


@login_required
def bookmarks(request):
    posts = Post.objects.bookmarked_by(request.user).with_full_details(request.user)
    page_obj = paginate_queryset(request, posts)
    return render(request, "feed/bookmarks.html", {"posts_page": page_obj})


@login_required
def new_post(request):
    if request.method == "GET":
        return render(request, "feed/new_post.html")

    body = request.POST.get("body", "").strip()
    if body:
        post = Post.objects.create(author=request.user, body=body)
        messages.success(request, "Post shared successfully.")
        return redirect("feed:post", post_id=post.id)
    return redirect("feed:index")


@require_POST
@csrf_exempt
def repost(request, post_id):
    """Create a pure repost (no body)."""

    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "401", "response": "Log in to perform this action"}
        )

    post = get_object_or_404(Post, id=post_id)
    if post.is_repost:
        messages.warning(request, "Cannot repost a repost. Use the original post.")
        return JsonResponse(
            {
                "status": "400",
                "error": "Cannot repost a repost. Use the original post.",
            },
        )

    repost, created = Post.objects.get_or_create(
        author=request.user, parent=post, body=""
    )

    if not created:
        repost.delete()
        action = "Reposted"
        messages.success(request, "Repost removed successfully.")
    else:
        action = "Repost removed"
        messages.success(request, "Post reposted successfully.")

    return JsonResponse(
        {
            "status": "201",
            "action": action,
        }
    )


@login_required
def quote(request, post_id):
    """Create a quote post (with body)."""

    post = get_object_or_404(Post, id=post_id)
    if post.is_repost:
        messages.error(request, "Cannot quote a repost.")
        return redirect("feed:post", post_id=post_id)

    if request.method == "GET":
        return render(request, "feed/new_quote.html", {"parent_post": post})

    body = request.POST.get("body", "").strip()
    if body:
        quote_post = Post.objects.create(author=request.user, parent=post, body=body)
        messages.success(request, "Quote shared successfully.")
        return redirect("feed:post", post_id=quote_post.id)

    messages.warning(request, "Quote body cannot be empty.")
    return redirect("feed:quote", post_id=post_id)


@require_POST
@csrf_exempt
def edit_post(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "401", "response": "Log in to perform this action"}
        )

    post = get_object_or_404(Post, pk=post_id, author=request.user)
    data = json.loads(request.body)
    post.body = data.get("body", "")
    post.save()
    return JsonResponse({"status": "201", "postContent": post.body})


@require_POST
@csrf_exempt
def delete_post(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "401", "response": "Log in to perform this action"}
        )

    post = get_object_or_404(Post, pk=post_id, author=request.user)
    post.delete()
    return JsonResponse({"status": "201", "action": f"Deleted post: {post_id}"})


@login_required
@require_POST
def comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.is_repost:
        messages.error(request, "Cannot comment on a repost.")
        return redirect("feed:post", post_id=post_id)

    body = request.POST.get("body", "").strip()
    if body:
        Comment.objects.create(post=post, author=request.user, body=body)
    return redirect("feed:post", post_id=post_id)


@require_POST
@csrf_exempt
def connect(request, username):
    """
    Follow or unfollow a user.
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "401", "response": "Log in to perform this action"}
        )

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


@require_POST
@csrf_exempt
def react(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "401", "response": "Log in to perform this action"}
        )

    post = get_object_or_404(Post, pk=post_id)
    if post.is_repost:
        return JsonResponse(
            {
                "status": "400",
                "error": "Cannot react to a repost.",
            },
            status=400,
        )

    reaction, created = Reaction.objects.get_or_create(user=request.user, post=post)

    if not created:
        reaction.delete()
        action = "Unliked"
    else:
        action = "Liked"

    return JsonResponse(
        {
            "status": "201",
            "action": action,
            "postReactionsCount": post.reactions.count(),
        }
    )


@require_POST
@csrf_exempt
def bookmark(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "401", "response": "Log in to perform this action"}
        )

    post = get_object_or_404(Post, pk=post_id)
    if post.is_repost:
        return JsonResponse(
            {
                "status": "400",
                "error": "Cannot bookmark a repost.",
            },
            status=400,
        )

    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)

    if not created:
        bookmark.delete()
        action = "Bookmark Removed"
    else:
        action = "Bookmarked"

    return JsonResponse({"status": "201", "action": action})


@require_POST
@csrf_exempt
def pin_post(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "401", "response": "Log in to perform this action"}
        )

    post = get_object_or_404(Post, pk=post_id, author=request.user)
    if post.is_repost:
        return JsonResponse(
            {
                "status": "400",
                "error": "Cannot pin a repost.",
            },
            status=400,
        )

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
