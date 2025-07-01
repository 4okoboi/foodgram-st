from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import User, Subscription


class BaseUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(subscriber=request.user, author=obj).exists()
        return False


class UserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'is_subscribed')


class UsersRecipesSerializer(BaseUserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar', 'is_subscribed', 'recipes_count', 'recipes'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit') if request else None
        queryset = obj.recipes.all()
        if recipes_limit is not None:
            try:
                limit = int(recipes_limit)
                queryset = queryset[:limit]
            except ValueError:
                pass
        from recipes.serializers import RecipeInUserSerializer
        serializer = RecipeInUserSerializer(queryset, many=True, context=self.context)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class SetAvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
