from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from djoser.views import UserViewSet
from .serializers import (
    CustomUserSerializer,
    SubscribeSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeGetSerializer,
    RecipeCreateSerializer,
    ShoppingCartSerializer,
    FavoriteRecipeSerializer,
)
from users.models import User, Subscribe
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.decorators import action
from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    FavoriteRecipe,
    ShoppingCart,
    IngredientsRecipe,
)
from django_filters.rest_framework import DjangoFilterBackend
from .filters import IngredientFilter, RecipeFilter
from .permission import AuthorOrReadOnly
from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse


class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователя и подписок"""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AuthorOrReadOnly,)

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
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
        serializer = SubscribeSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингридиентов"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов"""

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
        if self.action in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = (
            IngredientsRecipe.objects.filter(
                recipe__shopping_cart__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(sum_amount=Sum("amount"))
        )

        today = datetime.today()
        shopping_list = (
            f"Список покупок для: {user.get_full_name()}\n\n"
            f"Дата создания: {today:%Y-%m-%d}\n\n"
        )
        shopping_list += "\n".join(
            [
                f'- {ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f' - {ingredient["sum_amount"]}'
                for ingredient in ingredients
            ]
        )
        shopping_list += f"\n\nПриятного аппетита! (© FoodGram {today:%Y})"

        filename = f"{user.username}_shopping_list.txt"
        response = HttpResponse(shopping_list, content_type="text/plain")
        response["Content-Disposition"] = f"attachment; filename={filename}"

        return response


class ShoppingCartViewSet(
    mixins.DestroyModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """Вьюсет для списка покупок"""

    queryset = ShoppingCart.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ShoppingCartSerializer

    def create(self, request, *args, **kwargs):
        data = {"user": request.user.id, "recipe": self.kwargs.get("id")}
        serializer = ShoppingCartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        obj = ShoppingCart.objects.filter(
            user_id=request.user.id, recipe_id=self.kwargs.get("id")
        )
        if obj:
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            "Такого рецепта нет в корзине", status=status.HTTP_400_BAD_REQUEST
        )


class FavoriteRecipeViewSet(
    mixins.DestroyModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """Вьюсет для избранного"""

    queryset = FavoriteRecipe.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = FavoriteRecipeSerializer

    def create(self, request, *args, **kwargs):
        data = {"user": request.user.id, "recipe": self.kwargs.get("id")}
        serializer = FavoriteRecipeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        obj = FavoriteRecipe.objects.filter(
            user_id=request.user.id, recipe_id=self.kwargs.get("id")
        )
        if obj:
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            "Такого рецепта нет в избранном",
            status=status.HTTP_400_BAD_REQUEST,
        )
