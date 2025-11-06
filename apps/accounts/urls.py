from django.urls import path
from . import views


app_name = "accounts"

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("settings/", views.settings, name="settings"),
    path("settings/change-email", views.change_email, name="change-email"),
    path("settings/change-password", views.change_password, name="change-password"),
    path(
        "settings/deactivate-account",
        views.deactivate_account,
        name="deactivate-account",
    ),
]
