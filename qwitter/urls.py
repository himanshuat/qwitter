from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.accounts.urls", namespace="accounts")),
    path("feed/", include("apps.feed.urls", namespace="feed")),
    path("api/auth/", include("apps.core.api.urls", namespace="auth_api")),
    path("api/", include("apps.accounts.api.urls", namespace="accounts_api")),
    path("api/", include("apps.feed.api.urls", namespace="feed_api")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]


handler400 = "apps.core.views.error_400_view"
handler403 = "apps.core.views.error_403_view"
handler404 = "apps.core.views.error_404_view"
handler500 = "apps.core.views.error_500_view"
