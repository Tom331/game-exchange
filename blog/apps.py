from django.apps import AppConfig

print('~~~top of blog/apps.py~~~')

#BlogConfig inherits from AppConfig
class BlogConfig(AppConfig):
    name = 'blog'

print('~~~bottom of blog/apps.py~~~')
