from django.contrib import admin
from django.urls import include, path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("apps.accounts.urls", namespace="accounts")),
    path("feed", include("apps.feed.urls", namespace="feed")),
]

urlpatterns += staticfiles_urlpatterns()