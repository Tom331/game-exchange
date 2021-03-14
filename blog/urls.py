from django.urls import path
from .views import (
    PostListView,
    GameListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView
)
from . import views

urlpatterns = [
    #the 'name' param can be referenced in html. eg) href="{% url 'blog-home' %}". This allows us to avoid hard-coding
    path('', GameListView.as_view(), name='blog-home'),
    # path('', PostListView.as_view(), name='blog-home'), # old home page
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'), # <str:username> captures a string value from the username param in the URL
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='blog-about'),
]
