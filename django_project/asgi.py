# mysite/asgi.py
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, get_default_application
import chat.routing

print('~~~ACTUALLY(lol just a rebuild thing) in asgi ~~~')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")

application = ProtocolTypeRouter({
  "http": django_asgi_app, # TODO: CONFIRM http vs https
  "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})

