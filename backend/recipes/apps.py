import os
from django.apps import AppConfig


class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'

    # загрузка долгая, поэтому убрал постоянную. можно оптимизировать с помощью bulk_create
    # def ready(self):
    #     if os.environ.get('RUN_MAIN') == 'true':
    #         from django.core.management import call_command
    #         try:
    #             call_command('load_ingredients')
    #         except Exception as e:
    #             print(f'Ошибка при автозагрузке ингредиентов: {e}')
