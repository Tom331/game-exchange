from django.contrib import admin
# from .models import Profile, MyUser
from .models import MyUser

from django.contrib.auth import get_user_model
User = get_user_model()


print('~~~top of users/admin.py~~~')

# admin.site.register(Profile)
admin.site.register(MyUser) #<- THIS IS REGISTERING THE WRONG USER MODEL

class MyUserAdmin(admin.ModelAdmin): # override
    actions = ['delete_selected']
    def delete_selected( self, request, queryset ):
        queryset.delete()


print('~~~bottom of users/models.py~~~')
