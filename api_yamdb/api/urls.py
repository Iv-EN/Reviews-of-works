from django.urls import include, path
from rest_framework import routers

from . import views
from .views import CategoryViewSet, GenreViewsSet, TitleViewSet

router_v1 = routers.DefaultRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewsSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path(
        'redoc/', views.redoc,
        name='redoc'
    ),
    path('v1/', include(router_v1.urls)),
]
