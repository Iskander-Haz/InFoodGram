from .views import CustomUserViewSet, IngredientViewSet, TagViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register("users", CustomUserViewSet, basename="users")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("tags", TagViewSet, basename="tags")

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
