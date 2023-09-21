from django.urls import reverse
from colorfield.fields import ColorField
from django.db import models
from users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название ингредиента")
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
    name = models.CharField(max_length=200, unique=True, verbose_name="Название")
    color = ColorField(unique=True, format="hex", verbose_name="Цвет")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Слаг")

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Тег",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes", verbose_name="Автор"
    )
    name = models.CharField(max_length=200, verbose_name="Название рецепта")
    image = models.ImageField(upload_to="recipes/", verbose_name="Картинка")
    text = models.TextField(verbose_name="Текстовое описание рецепта")
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(1, message="Время не может быть меньше 1 мин."),
            MaxValueValidator(30240, message="Нельзя готовить дольше 3х недель!"),
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

    def __str__(self):
        return self.name


class IngredientsRecipe(models.Model):
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
            MinValueValidator(1, message="Количество не может быть меньше 1"),
            MaxValueValidator(32000, message="Количество не может быть меньше 32000"),
        ],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="unique_recipe_ingredient"
            ),
        ]

    def __str__(self):
        return f"{self.recipe} - {self.ingredient} - {self.amount}"


class FavoriteRecipe(models.Model):
    """Мдель избранных рецептов"""

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
        return f"{self.user.first_name} - {self.user.last_name} - {self.recipe.name}"


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
                fields=["user", "recipe"], name="unique_user_recipe_shopping_cart"
            ),
        ]

    def __str__(self):
        return f"{self.user.first_name} - {self.user.last_name} - {self.recipe.name}"
