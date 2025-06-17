from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.db import IntegrityError
from .models import User


def login_view(request):
	if request.user.is_authenticated:
		return HttpResponse(f"Logged in as {request.user}.")

	if request.method == "POST":
		username = request.POST.get("username", "").lower()
		password = request.POST.get("password", "")
		user = authenticate(request, username=username, password=password)

		if user:
			login(request, user)
			messages.success(request, "Logged in successfully.")
			return HttpResponse(f"✅ Welcome back, {user.name}!")
		else:
			messages.error(request, "Invalid username or password.")

	return render(request, "accounts/login.html")

def logout_view(request):
	logout(request)
	messages.info(request, "You've been logged out.")
	return HttpResponse("👋 Logged out successfully!")

def register(request):
	if request.user.is_authenticated:
		return HttpResponse("Already registered and logged in.")

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
			messages.success(request, "Account created and logged in.")
			return HttpResponse(f"🎉 Welcome to Qwitter, {user.name}!")
		except IntegrityError:
			messages.error(request, "Username or email already taken.")
			return render(request, "accounts/register.html")
	return render(request, "accounts/register.html")
