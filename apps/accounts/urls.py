from django.urls import path
from . import views


app_name = "accounts"

urlpatterns = [
	path("login/", views.login_view, name="login"),
	path("logout/", views.logout_view, name="logout"),
	path("register/", views.register, name="register"),
	path("profile/edit/", views.edit_profile, name="edit_profile"),
	path("profile/<str:username>/", views.profile, name="profile"),
]
