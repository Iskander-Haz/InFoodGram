from rest_framework.exceptions import ValidationError
from rest_framework import serializers, status
from djoser.serializers import UserSerializer
from users.models import User, Subscribe
from recipes.models import Ingredient, Tag, Recipe, IngredientsRecipe
from drf_extra_fields.fields import Base64ImageField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.transaction import atomic


class CustomUserSerializer(UserSerializer):
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
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ("recipes_count", "recipes")
        read_only_fields = ("email", "username")

    def validate(self, data):
        author = self.instance
        user = self.context.get("request").user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail="Нельзя подписаться на автора повторно!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail="Нельзя подписаться на самого себя!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = IngredientsRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True, source="ingredients_recipe")
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
        return user.is_authenticated and user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        return user.is_authenticated and user.shopping_cart.filter(recipe=obj).exists()


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(32000)]
    )

    class Meta:
        model = IngredientsRecipe
        fields = ("id", "amount")


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30240)]
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
            raise serializers.ValidationError({"tags": "Укажите хотя бы один тег!"})
        if len({tag.id for tag in data.get("tags")}) != len(data.get("tags")):
            raise serializers.ValidationError({"tags": "Такой тег уже указан!"})
        if not data.get("ingredients"):
            raise serializers.ValidationError(
                {"ingredients": "Укажите ингридиенты для приготовления блюда!"}
            )
        if len({ingredient["id"] for ingredient in data.get("ingredients")}) != len(
            data.get("ingredients")
        ):
            raise serializers.ValidationError(
                {"ingredients": "Такой ингридиент уже добавлен!"}
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
        return RecipeReadSerializer(instance, context=self.context).data