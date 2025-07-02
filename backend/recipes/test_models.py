import pytest
from django.contrib.auth import get_user_model
from .models import Recipe, RecipeIngredient, Ingredient  

@pytest.mark.django_db
def test_create_recipe_with_ingredient():
    User = get_user_model()
    
    user = User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123'
    )
    
    ingredient = Ingredient.objects.create(
        name='Сахар',
        measurement_unit='г'
    )
    
    recipe = Recipe.objects.create(
        author=user,
        name='Торт',
        text='Смешать и испечь.',
        cooking_time=30,
        image='recipes/images/test.jpg' 
    )
    
    recipe_ingredient = RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=ingredient,
        amount=100
    )
    
    assert recipe.author == user
    assert recipe.name == 'Торт'
    assert recipe.cooking_time == 30
    assert recipe_ingredient.ingredient == ingredient
    assert recipe_ingredient.amount == 100

    assert str(recipe) == 'Торт'
    assert str(recipe_ingredient) == 'Сахар — 100 г.'
