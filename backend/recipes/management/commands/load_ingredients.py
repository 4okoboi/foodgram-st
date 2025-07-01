import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient
from pathlib import Path

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        json_path = '../data/ingredients.json'
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)
        for item in data:
            Ingredient.objects.get_or_create(
                name=item['name'],
                defaults={'measurement_unit': item['measurement_unit']}
            )
        self.stdout.write(self.style.SUCCESS('Ingredients loaded successfully'))
