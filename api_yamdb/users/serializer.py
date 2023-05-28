from django.contrib.auth import get_user_model
from rest_framework import serializers

from api_yamdb.settings import USERNAME_NAME, EMAIL
from .validators import ValidateUsername


User = get_user_model()


class UserCreateSerializer(serializers.Serializer, ValidateUsername):
    class Meta:
        model = User
        fields = ('username', 'email')


class BaseUserSerializer(serializers.ModelSerializer, ValidateUsername):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        read_only_fields = ('role',)


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        read_only_fields = ()

    def validate_role(self, role):
        req_user = self.context['request'].user
        user = User.objects.get(username=req_user)

        if user.is_moderator:
            if role != 'admin':
                role = 'admin'
        elif user.is_user:
            role = user.role
        return role


class RegistrationSerializer(serializers.Serializer, ValidateUsername):
    username = serializers.CharField(required=True, max_length=USERNAME_NAME)
    email = serializers.EmailField(required=True, max_length=EMAIL)


class TokenSerializer(serializers.Serializer, ValidateUsername):
    username = serializers.CharField(required=True, max_length=USERNAME_NAME)
    confirmation_code = serializers.CharField(required=True)


class UserEditSerializer(UserSerializer):
    """Сериализатор модели User для get и patch"""

    role = serializers.CharField(read_only=True)
