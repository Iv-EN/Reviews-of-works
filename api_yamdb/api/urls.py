from django.urls import include, path
from rest_framework import routers

from . import views
from .views import (CategoryViewSet, CommentViewSet, GenreViewsSet,
                    ReviewViewSet, TitleViewSet, UserViewSet, create_token,
                    create_user)

router_v1 = routers.DefaultRouter()

router_v1.register('users', UserViewSet)
router_v1.register(
    'categories',
    CategoryViewSet,
    basename='categories')
router_v1.register(
    'genres',
    GenreViewsSet,
    basename='genres')
router_v1.register(
    'titles',
    TitleViewSet,
    basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments')

urls_auth = [
    path('auth/signup/', create_user, name='create_user'),
    path('auth/token/', create_token, name='create_token'),
]

urlpatterns = [
    path('v1/', include(urls_auth)),
    path('v1/', include(router_v1.urls)),
    path(
        'redoc/', views.redoc,
        name='redoc'
    ),
    path('v1/', include(router_v1.urls)),
]
