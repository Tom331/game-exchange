from django.apps import AppConfig

print('~~~top of users/apps.py~~~')

class UsersConfig(AppConfig):
    name = 'users'

    # def ready(self):
    #     import users.signals

print('~~~bottom of users/apps.py~~~')
