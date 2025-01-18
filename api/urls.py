from django.urls import include, path
from rest_framework.routers import SimpleRouter
from . import views


router = SimpleRouter()
router.register('posts', views.PostViewSet)


app_name = 'api'


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('', include(router.urls)),
]
