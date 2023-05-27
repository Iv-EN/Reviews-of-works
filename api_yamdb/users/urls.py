from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet, create_user, create_token

router_v1 = routers.DefaultRouter()
router_v1.register('users', UserViewSet)

api_v1_urls = [
    path('auth/signup/', create_user, name='create_user'),
    path('auth/token/', create_token, name='create_token'),
]


urlpatterns = [
    path('v1/', include(api_v1_urls)),
    path('v1/', include(router_v1.urls)),
]
