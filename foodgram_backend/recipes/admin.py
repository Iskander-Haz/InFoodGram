from django.contrib import admin
from .models import (
    Ingredient,
    Tag,
    Recipe,
    IngredientsRecipe,
    FavoriteRecipe,
    ShoppingCart,
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_filter = ("name",)


class IngredientInline(admin.TabularInline):
    model = IngredientsRecipe
    min_num = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author")
    list_filter = ("name", "author")

    inlines = [
        IngredientInline,
    ]


@admin.register(IngredientsRecipe)
class IngredientsRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass
