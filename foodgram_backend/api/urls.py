from .views import (
    CustomUserViewSet,
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    FavoriteRecipeViewSet,
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register("users", CustomUserViewSet, basename="users")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("tags", TagViewSet, basename="tags")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register(
    "recipes/(?P<id>[^/.]+)/shopping_cart",
    ShoppingCartViewSet,
    basename="shopping_cart",
)
router.register(
    "recipes/(?P<id>[^/.]+)/favorite", FavoriteRecipeViewSet, basename="favorite"
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
