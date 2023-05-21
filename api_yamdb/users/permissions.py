from rest_framework.permissions import BasePermission, SAFE_METHODS


class AdminAndSuperuserOnly(BasePermission):
    """Разрешение доступа только администратору/суперпользователю"""

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.is_admin or user.is_superuser)


class AuthenticatedPrivilegedUsersOrReadOnly(BasePermission):
    """Разрешение доступа на чтение всем и
    на редактирование только
    аутентифицированным пользователям"""

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            request.method in SAFE_METHODS
            or obj.author == user
            or user.is_admin
            or user.is_superuser
            or user.is_moderator
        )


class ListOrAdminModeratOnly(BasePermission):
    """Разрешает получения списка всем и редактирование
    только  администратору/суперпользователю"""

    def has_permission(self, request, view):
        user = request.user
        return (
            request.method in SAFE_METHODS
            or user.is_superuser
            or (user.is_authenticated and user.is_admin)
        )
