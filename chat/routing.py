# chat/routing.py
from django.urls import re_path
from django.core.asgi import get_asgi_application
from . import consumers

print('~~~IN ROUTING.PY~~~')

websocket_urlpatterns = [
    # apply the consumer to handle the websocket connection. This will listen for the 3 events in consumers.py
    #re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer), #old django
    re_path(r'^ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()), #new django
    #re_path(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer),
]