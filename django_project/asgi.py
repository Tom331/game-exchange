# mysite/asgi.py
import os
import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, get_default_application
from django.core.asgi import get_asgi_application
import chat.routing

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
# django.setup() #crit
# startapp = get_default_application() #todo: confirm why app doesn't crash if this is commented out... this is called from Procfile
print('~~~in asgi~~~')
application = ProtocolTypeRouter({ #
  "http": get_asgi_application(), # TODO: CONFIRM http vs https
  "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})