from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    amount = serializers.IntegerField(
        min_value=1,
        error_messages={
            'min_value': "Amount must be greater than 0"
        }
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeInUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeListSerializer(serializers.ModelSerializer):
    from users.serializers import UserSerializer
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(source='recipe_ingredients', many=True, read_only=True)
    is_favourite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favourite', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favourite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()
        return False



class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(
        required=True,
        allow_null=False,
        min_length=1,
        many=True,
        error_messages={
            'required': 'Field is required',
            'null': "Field can't be null",
            'min_length': "List can't be empty"
        },
        write_only=True
    )
    image = Base64ImageField(
        required=True,
        allow_null=False,
        error_messages={
            'required': 'Field is required',
            'null': "Field can't be empty"
        }
    )

    cooking_time = serializers.IntegerField(
        min_value=1,
        required=True,
        allow_null=False,
        error_messages={
            "min_value": "Field must be greater than 0"
        }
    )

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'image', 'name', 'text', 'cooking_time')

    def validate_ingredients(self, value):
        seen_ids = set()

        for ingredient in value:
            ing_id = ingredient.get('id')

            if ing_id in seen_ids:
                raise serializers.ValidationError(f"Ingredient with id {ing_id} is duplicated.")
            seen_ids.add(ing_id)

            if not Ingredient.objects.filter(id=ing_id).exists():
                raise serializers.ValidationError(f"Ingredient with id {ing_id} does not exist.")

        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        return recipe

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        instance.recipe_ingredients.all().delete()
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )

        return instance