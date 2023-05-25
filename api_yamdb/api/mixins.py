from rest_framework import mixins, viewsets


class ModelMixinSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Обработка GET, POST и DELETE запросов для объектов Category и Genre.
    """
