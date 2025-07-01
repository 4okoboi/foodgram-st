from django.db import models
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    measurement_unit = models.CharField(max_length=64)

    class Meta:
        unique_together = ('name', 'measurement_unit')
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f"{self.name} ({self.measurement_unit}.)"

class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='recipes/images/', storage=S3Boto3Storage())
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()
    load_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-load_date']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.PositiveIntegerField()

    class Meta:
        unique_together = ('recipe', 'ingredient')
        verbose_name = 'Ingredient in recipe'
        verbose_name_plural = 'Ingredients in recipes'

    def __str__(self):
        return f"{self.ingredient.name} — {self.amount} {self.ingredient.measurement_unit}."

class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Favourite'
        verbose_name_plural = 'Favourites'

    def __str__(self):
        return f"{self.user.username} added {self.recipe.name} to favourites"

class ShoppingCart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Shopping cart'
        verbose_name_plural = 'Shopping carts'

    def __str__(self):
        return f"{self.user.username} added {self.recipe.name} to shopping cart"