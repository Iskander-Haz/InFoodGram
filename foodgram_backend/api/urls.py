from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomUserViewSet,
    FavoriteRecipeViewSet,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    TagViewSet,
)

router = DefaultRouter()

router.register("users", CustomUserViewSet, basename="users")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("tags", TagViewSet, basename="tags")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register(
    r"recipes/(?P<id>\d+)/favorite", FavoriteRecipeViewSet, basename="favorite"
)
router.register(
    r"recipes/(?P<id>\d+)/shopping_cart",
    ShoppingCartViewSet,
    basename="shopping_cart",
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
