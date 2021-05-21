
from django.urls import path, include
from . import views

app_name = 'chat'

urlpatterns = [
    path('chat/', views.index, name='index'),
    path('chat/<str:room_name>/', views.room, name='room'),
]
