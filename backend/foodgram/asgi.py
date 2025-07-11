import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import api.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            api.routing.websocket_urlpatterns
        )
    ),
})
