from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required

from .models import User
from apps.feed.models import Post
from apps.core.utils import paginate_queryset


def index(request):
	return redirect("feed:index")


def login_view(request):
	if request.user.is_authenticated:
		return redirect("feed:index")

	if request.method == "POST":
		username = request.POST.get("username", "").lower()
		password = request.POST.get("password", "")
		user = authenticate(request, username=username, password=password)

		if user:
			login(request, user)
			messages.success(request, "Logged in successfully.")
			return redirect("feed:index")
		else:
			messages.error(request, "Invalid username or password.")

	return render(request, "accounts/login.html")


def logout_view(request):
	logout(request)
	messages.info(request, "You've been logged out.")
	return redirect("feed:index")


def register(request):
	if request.user.is_authenticated:
		return redirect("feed:index")

	if request.method == "POST":
		username = request.POST.get("username", "").lower()
		email = request.POST.get("email", "")
		password = request.POST.get("password", "")
		confirmation = request.POST.get("confirmation", "")
		name = request.POST.get("name", "")

		if password != confirmation:
			messages.warning(request, "Passwords do not match.")
			return render(request, "accounts/register.html")
		
		try:
			user = User.objects.create_user(
				username=username,
				email=email,
				password=password,
				name=name
			)
			login(request, user)
			messages.success(request, "Registration successful. Please complete your profile.")
			return redirect("accounts:edit_profile")
		except IntegrityError:
			messages.error(request, "Username or email already taken.")
			return render(request, "accounts/register.html")
	
	return render(request, "accounts/register.html")


def profile(request, username):
    user = get_object_or_404(User, username__iexact=username)

    posts = Post.objects.for_user(user).order_by("-is_pinned", "-created_date")
    page_obj = paginate_queryset(request, posts)

    return render(request, "accounts/profile.html", {
        "profile_user": user,
        "posts_page": page_obj,
    })


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

