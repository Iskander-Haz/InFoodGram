from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.transaction import atomic
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from recipes.models import (FavoriteRecipe, Ingredient, IngredientsRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Subscribe, User

MIN_VALUE_COOKING_TIME = 1
MAX_VALUE_COOKING_TIME = 32000
MIN_VALUE_AMOUNT = 1
MAX_VALUE_AMOUNT = 32000


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя"""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        return user.is_authenticated and bool(
            Subscribe.objects.filter(user=user, author=obj)
        )


class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор подписок"""

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )
        read_only_fields = ("email", "username")

    def validate(self, data):
        author = self.instance
        user = self.context.get("request").user
        # if Subscribe.objects.filter(author=author, user=user).exists():
        if author.subscribing.filter(user=user).exists():
            raise ValidationError(
                detail="Вы не можете подписаться на автора повторно!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail="Вы не можете подписаться на самого себя!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        return RecipeShowSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов"""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов в рецепте"""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientsRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов"""

    author = CustomUserSerializer()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source="ingredients_recipe"
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and user.shopping_cart.filter(recipe=obj).exists()
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов при создании рецепта"""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_VALUE_AMOUNT),
            MaxValueValidator(MAX_VALUE_AMOUNT),
        ]
    )

    class Meta:
        model = IngredientsRecipe
        fields = ("id", "amount")


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания/изминения рецепта"""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_VALUE_COOKING_TIME),
            MaxValueValidator(MAX_VALUE_COOKING_TIME),
        ]
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )

    def validate(self, data):
        if not data.get("tags"):
            raise serializers.ValidationError(
                {"tags": "Вы не можете не указать тег!"}
            )
        if len(set(data.get("tags"))) != len(data.get("tags")):
            raise serializers.ValidationError(
                {"tags": "Вы уже указали такой тег!"}
            )
        if not data.get("ingredients"):
            raise serializers.ValidationError(
                {"ingredients": "Вы не можете не добавить ингридиент!"}
            )
        if len(
            {ingredient["id"] for ingredient in data.get("ingredients")}
        ) != len(data.get("ingredients")):
            raise serializers.ValidationError(
                {"ingredients": "Вы уже добавили такой ингридиент!"}
            )
        return data

    def create_tags_ingredients(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        ingredients_list = []
        for ingredient in ingredients:
            ingredients_list.append(
                IngredientsRecipe(
                    recipe=recipe,
                    ingredient=ingredient["id"],
                    amount=ingredient["amount"],
                )
            )
        IngredientsRecipe.objects.bulk_create(ingredients_list)

    @atomic
    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(
            author=self.context["request"].user, **validated_data
        )
        self.create_tags_ingredients(recipe, tags, ingredients)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        instance.image = validated_data.get("image", instance.image)
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        instance.ingredients.clear()
        self.create_tags_ingredients(instance, tags, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeGetSerializer(instance, context=self.context).data


class RecipeShowSerializer(serializers.ModelSerializer):
    """Сериализатор для сокращенного показа
    рецептов в подписках/избранном/списке покупок"""

    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок"""

    class Meta:
        model = ShoppingCart
        fields = (
            "user",
            "recipe",
        )

    def validate(self, data):
        user = data["user"]
        if user.shopping_cart.filter(recipe_id=data["recipe"]).exists():
            raise serializers.ValidationError(
                {"shopping_cart": "Рецепт уже добавлен!"}
            )
        return data

    def to_representation(self, instance):
        return RecipeShowSerializer(instance.recipe).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор избранного"""

    class Meta:
        model = FavoriteRecipe
        fields = (
            "user",
            "recipe",
        )

    def validate(self, data):
        user = data["user"]
        if user.favorites.filter(recipe_id=data["recipe"]).exists():
            raise serializers.ValidationError(
                {"favorite": "Рецепт уже добавлен!"}
            )
        return data

    def to_representation(self, instance):
        return RecipeShowSerializer(instance.recipe).data
