from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Что бы изменить данный контент нужно быть админом."""
