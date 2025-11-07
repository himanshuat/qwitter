from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError

from .models import User
from apps.feed.models import Post
from apps.core.utils import paginate_queryset


def index(request):
    return redirect("feed:index")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("feed:index")

    if request.method == "GET":
        return render(request, "accounts/login.html")

    username = request.POST.get("username", "").lower()
    password = request.POST.get("password", "")
    user = authenticate(request, username=username, password=password)

    if user:
        login(request, user)
        messages.success(request, "Logged in successfully.")

        next_url = request.POST.get("next") or request.GET.get("next")
        if next_url:
            return redirect(next_url)
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        messages.error(request, "Invalid username or password.")
        return redirect(settings.LOGIN_REDIRECT_URL)


def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out.")
    return redirect(settings.LOGOUT_REDIRECT_URL)


def register(request):
    if request.user.is_authenticated:
        return redirect("feed:index")

    if request.method == "POST":
        username = request.POST.get("username", "").strip().lower()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirmation = request.POST.get("confirmation", "")
        name = request.POST.get("name", "").strip()

        if not all([username, email, password, confirmation, name]):
            messages.error(request, "All fields are required.")
            return render(request, "accounts/register.html")

        if password != confirmation:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/register.html")

        try:
            validate_password(
                password, user=User(username=username, email=email, name=name)
            )
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, "accounts/register.html")

        try:
            user = User.objects.create_user(
                username=username, email=email, password=password, name=name
            )
            login(request, user)
            messages.success(
                request, "Welcome! Your account has been created successfully."
            )
            return redirect("accounts:edit_profile")
        except IntegrityError:
            messages.error(
                request, "An account with this username or email already exists."
            )
            return render(request, "accounts/register.html")

    return render(request, "accounts/register.html")


def profile(request, username):
    user = get_object_or_404(User, username__iexact=username)

    posts = Post.objects.for_user(user).order_by("-is_pinned", "-created_date")
    page_obj = paginate_queryset(request, posts)

    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": user,
            "posts_page": page_obj,
        },
    )


@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        user.name = request.POST.get("name", "").strip()
        user.image = request.POST.get("image", "").strip()
        user.dob = request.POST.get("dob") or None
        user.bio = request.POST.get("bio", "").strip()
        user.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("accounts:profile", username=user.username)

    return render(request, "accounts/edit_profile.html")


def account_settings(request):
    return render(request, "accounts/settings.html")


@login_required
def change_email(request):
    """
    Allow authenticated users to update their email address.
    """
    if request.method == "GET":
        return render(request, "accounts/change_email.html")

    new_email = request.POST.get("new-email")
    password = request.POST.get("password")

    if not new_email or not password:
        messages.warning(request, "Both email and password are required.")
        return redirect("accounts:change-email")

    if not request.user.check_password(password):
        messages.error(request, "Incorrect password. Please try again.")
        return redirect("accounts:change-email")

    if new_email == request.user.email:
        messages.info(request, "This is already your current email address.")
        return redirect("accounts:change-email")

    request.user.email = new_email
    request.user.save()

    messages.success(request, "Email address updated successfully.")
    return redirect("accounts:settings")


@login_required
def change_password(request):
    """
    Allow authenticated users to change their password.
    """
    if request.method == "GET":
        return render(request, "accounts/change_password.html")

    old_password = request.POST.get("old-password")
    new_password = request.POST.get("new-password")

    if not old_password or not new_password:
        messages.warning(request, "Both old and new passwords are required.")
        return redirect("accounts:change-password")

    if not request.user.check_password(old_password):
        messages.error(request, "Incorrect old password. Please try again.")
        return redirect("accounts:change-password")

    request.user.set_password(new_password)
    request.user.save()

    messages.success(request, "Password changed successfully. Please log in again.")
    return redirect("accounts:logout")


@login_required
def deactivate_account(request):
    """
    Deactivate (soft delete) the user's account.
    """
    if request.method == "GET":
        return render(request, "accounts/deactivate_account.html")

    password = request.POST.get("password")

    if not password:
        messages.warning(request, "Password is required to confirm deactivation.")
        return redirect("accounts:deactivate-account")

    if not request.user.check_password(password):
        messages.error(request, "Incorrect password. Please try again.")
        return redirect("accounts:deactivate-account")

    user = request.user
    user.is_active = False
    user.save()

    messages.success(
        request,
        f"Your account @{user.username} has been deactivated successfully. "
        "You can reactivate it later by contacting support.",
    )
    return redirect("accounts:logout")
