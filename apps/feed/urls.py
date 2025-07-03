from django.urls import path
from . import views

app_name = "feed"

urlpatterns = [
    path("", views.index, name="index"),
    path("following/", views.following, name="following"),
    
    path("posts/<int:post_id>/", views.post, name="post"),
    path("posts/<int:post_id>/comment/", views.comment, name="comment"),
    path("posts/<int:post_id>/edit/", views.edit_post, name="edit_post"),
    path("posts/<int:post_id>/delete/", views.delete_post, name="delete_post"),
    path("posts/<int:post_id>/react/", views.react, name="react"),
    path("posts/<int:post_id>/bookmark/", views.bookmark, name="bookmark"),
    path("posts/<int:post_id>/pin/", views.pin_post, name="pin_post"),

    path("posts/new/", views.new_post, name="new_post"),
    
    path("bookmarks/", views.bookmarks, name="bookmarks"),
    
    path("profile/<str:username>/connect/", views.connect, name="connect"),
]
