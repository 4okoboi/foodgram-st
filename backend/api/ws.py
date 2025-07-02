import json
from channels.generic.websocket import AsyncWebsocketConsumer

# Храним активные соединения
active_clients = set()


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


