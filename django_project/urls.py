"""django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views
from chat.views import index
from django.conf.urls import url


urlpatterns = [
    path('', include('chat.urls', namespace='chat')),
    path('account/', user_views.account, name='account'),
    path('account/delete/', user_views.delete_account, name='user-delete'), #  url to accept POST call from Your Trades page to delete a trade
    path('login/account/locked/', user_views.account_locked, name='account-locked'), # The url django-axes redirects to after too many failures
    path('admin/', admin.site.urls), #default "admin" page supplied by Django?
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'), # No title set for Google Analytics
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'), # No title set for Google Analytics

    # Email Activation/Opt-out
    re_path(r'^activate/(?P<key>.+)$', user_views.activation, name='activate'),
    path('new-activation-link/', user_views.new_activation_link, name='new-activation-link'),

    # link to /user-id/opt-out-key which sets user.confirmed_trade_email_opt_in to false. No login required
    path('confirmed-trade-opt-out/<int:pk>/<opt_out_key>', user_views.confirmed_trade_opt_out, name='confirmed-trade-opt-out'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),


    path('', include('blog.urls')),


    #~~~OLD~~~
    # path('profile/', user_views.profile, name='profile'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
