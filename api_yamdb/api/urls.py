from django.urls import path

from . import views

urlpatterns = [
    path(
        'redoc/', views.redoc,
        name='redoc'
    ),
]
