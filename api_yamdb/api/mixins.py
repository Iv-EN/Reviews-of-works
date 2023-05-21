from rest_framework import mixins, viewsets


class MixinsListCreateDestroyViewsSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Обработка GET, POST и DELETE запросов для объектов Category и Genre.
    """
