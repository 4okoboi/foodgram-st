import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

# Храним активные соединения
active_clients = set()

class RecipeStatsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("recipe_stats", self.channel_name)
        await self.accept()
        await self.push_recipe_count()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("recipe_stats", self.channel_name)

    async def push_recipe_count(self):
        from recipes.models import Recipe
        total_recipes = await sync_to_async(Recipe.objects.count)()
        await self.send(text_data=json.dumps({
            "recipes_total": total_recipes
        }))

    async def refresh_recipe_data(self, event):
        await self.push_recipe_count()


class OnlineUsersConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        active_clients.add(self.channel_name)
        await self.channel_layer.group_add("online_users", self.channel_name)
        await self.notify_user_count()

    async def disconnect(self, close_code):
        active_clients.discard(self.channel_name)
        await self.channel_layer.group_discard("online_users", self.channel_name)
        await self.notify_user_count()

    async def notify_user_count(self):
        total = len(active_clients)
        await self.channel_layer.group_send(
            "online_users",
            {
                "type": "update_user_count",
                "total": total
            }
        )

    async def update_user_count(self, event):
        await self.send(text_data=json.dumps({
            "users_online": event["total"]
        }))


