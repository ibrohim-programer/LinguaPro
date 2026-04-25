import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from apps.messages_app.middleware import JWTAuthMiddlewareStack
from apps.messages_app.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': JWTAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})