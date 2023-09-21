from rest_framework.response import Response
from rest_framework import status, viewsets
from djoser.views import UserViewSet
from .serializers import (
    CustomUserSerializer,
    SubscribeSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeReadSerializer,
    RecipeCreateSerializer,
)
from users.models import User, Subscribe
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from recipes.models import Ingredient, Tag, Recipe
from django_filters.rest_framework import DjangoFilterBackend
from .filters import IngredientFilter, RecipeFilter
from .permission import AuthorOrReadOnly


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(
        detail=True, methods=("post", "delete"), permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get("id")
        author = get_object_or_404(User, id=author_id)

        if request.method == "POST":
            serializer = SubscribeSerializer(
                author, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(Subscribe, user=user, author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ["get", "post", "patch", "create", "delete"]

    @staticmethod
    def create_object(serializer_class, pk, request):
        data = {"user": request.user.id, "recipe": pk}
        serializer = serializer_class(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeReadSerializer
        return RecipeCreateSerializer
