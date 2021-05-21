# mysite/routing.py

from .wsgi import *
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing

print('~~~top of django_project/routing.py~~~')

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns #references urls defined in chat/routing.py
        )
    ),
})

print('~~~bottom of django_project/routing.py~~~')
