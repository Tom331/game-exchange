from django.urls import path
from django.conf.urls import url
from .views import (
    PostListView,
    TradeListView,
    PostDetailView,
    TradeCreateView,
    GameAutoComplete,
    PostUpdateView,
    PostDeleteView,
    UserPostListView
)
from . import views

urlpatterns = [
    # the 'name' param can be referenced in html. eg) href="{% url 'blog-home' %}". This allows us to avoid hard-coding
    # params: path(route, view, kwargs=None, name=None)¶
    # route is a str that contains a url pattern
    # view is a view function or the result of a as_view() class. It can also be an django.urls.include()
    # The kwargs argument allows you to pass additional arguments to the view function or method.
    # name
    path('', views.home, name='blog-home'),
    path('matches/', TradeListView.as_view(), name='blog-matches'),
    # path('', PostListView.as_view(), name='blog-home'), # old home page
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'), # <str:username> captures a string value from the username param in the URL
    path('trade/<int:pk>/', PostDetailView.as_view(), name='blog-matches'),
    path('trade/new/', views.trade_new, name='trade-create'),
    url(
        r'^game-autocomplete/$',
        GameAutoComplete.as_view(),
        name='game-autocomplete'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='blog-about'),
]
