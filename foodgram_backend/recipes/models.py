from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User

MIN_VALUE_COOKING_TIME = 1
MAX_VALUE_COOKING_TIME = 32000
MIN_VALUE_AMOUNT = 1
MAX_VALUE_AMOUNT = 32000


class Ingredient(models.Model):
    """Модель ингридиента"""

    name = models.CharField(
        max_length=200, verbose_name="Название ингредиента"
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name="Единицы измерения"
    )

    class Meta:
        ordering = ("name",)
        unique_together = (
            "name",
            "measurement_unit",
        )

    def __str__(self):
        return f"{self.name} - {self.measurement_unit}"


class Tag(models.Model):
    """Модель тега"""

    name = models.CharField(
        max_length=200, unique=True, verbose_name="Название"
    )
    color = ColorField(unique=True, format="hex", verbose_name="Цвет")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Слаг")

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""

    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Тег",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(max_length=200, verbose_name="Название рецепта")
    image = models.ImageField(upload_to="recipes/", verbose_name="Картинка")
    text = models.TextField(verbose_name="Текстовое описание рецепта")
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(
                MIN_VALUE_COOKING_TIME,
                message="Время не может быть меньше 1 мин.",
            ),
            MaxValueValidator(
                MAX_VALUE_COOKING_TIME,
                message="Так долго готовить недопустимо!",
            ),
        ],
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        through="IngredientsRecipe",
        verbose_name="Ингредиенты",
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientsRecipe(models.Model):
    """Модель ингридиенты-рецепт"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients_recipe",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipes_ingredient",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        validators=[
            MinValueValidator(
                MIN_VALUE_AMOUNT, message="Количество не может быть меньше 1"
            ),
            MaxValueValidator(
                MAX_VALUE_AMOUNT,
                message="Количество не может быть больше 32000",
            ),
        ],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient",
            ),
        ]

    def __str__(self):
        return f"{self.recipe} - {self.ingredient} - {self.amount}"


class FavoriteRecipe(models.Model):
    """Модель избранных рецептов"""

    user = models.ForeignKey(
        User,
        related_name="favorites",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="favorites",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_recipe"
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.first_name}"
            f"- {self.user.last_name}"
            f"- {self.recipe.name}"
        )


class ShoppingCart(models.Model):
    """Модель корзины покупок"""

    user = models.ForeignKey(
        User,
        related_name="shopping_cart",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="shopping_cart",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_recipe_shopping_cart",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.first_name}"
            f"- {self.user.last_name}"
            f"- {self.recipe.name}"
        )
