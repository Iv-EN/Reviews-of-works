import random
from string import digits

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django_filters import rest_framework as filters

from .permissions import AdminAndSuperuserOnly
from .serializer import UserCreateSerializer, UserSerializer

User = get_user_model()


@api_view(['POST'])
def create_user(request):
    email = request.data.get('email')
    username = request.data.get('username')
    if (User.objects.filter(email=email).exists() and
            User.objects.filter(username=username).exists()):
        return Response(status=status.HTTP_200_OK)
    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    confirmation_code = ''.join(random.choices(digits, k=5))
    serializer.save(confirmation_code=confirmation_code)

    send_mail(
        subject='Регистрация на YaMDB',
        message=f'Ваш код для подтверждения регистрации: {confirmation_code}',
        from_email=settings.ADMIN_EMAIL,
        recipient_list=[request.data['email']]
    )

    return Response(serializer.data)


@api_view(['POST'])
def create_token(request):
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')

    if not username or not confirmation_code:
        return Response(
            'Одно или несколько обязательных полей пропущены',
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            'Имя пользователя неверное',
            status=status.HTTP_404_NOT_FOUND
        )

    if user.confirmation_code != confirmation_code:
        return Response(
            'Код подтверждения неверен',
            status=status.HTTP_400_BAD_REQUEST
        )

    token = AccessToken.for_user(user)
    return Response(
        {'access': str(token)}
    )


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = User.objects.all()
    permission_classes = (AdminAndSuperuserOnly,)
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=[IsAuthenticated, ]
    )
    def me_profile(self, request, pk=None):
        username = request.user.username
        user = User.objects.get(username=username)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                user, data=request.data,
                partial=True,
                context={'request': request}
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)   

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        search_username = request.query_params.get('search')
        if search_username:
            queryset = queryset.filter(username=search_username)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
