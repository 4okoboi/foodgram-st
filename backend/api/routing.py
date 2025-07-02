from django.urls import re_path

from . import ws

websocket_urlpatterns = [
    re_path(r"ws/users/$", ws.OnlineUsersConsumer.as_asgi()),
    re_path(r"ws/recipes/$", ws.RecipeStatsConsumer.as_asgi()),
]