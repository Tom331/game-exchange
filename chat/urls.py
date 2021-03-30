<<<<<<< HEAD

from django.urls import path, include
from . import views

app_name = 'chat'

urlpatterns = [
    path('chat/', views.index, name='index'),
    path('chat/<str:room_name>/', views.room, name='room'),
=======
# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:room_name>/', views.room, name='room'),
>>>>>>> f63def76365a5dbaf714975304c677ace7b3d167
]
