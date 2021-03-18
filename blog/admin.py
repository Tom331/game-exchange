from django.contrib import admin
from .models import Post, Game, Trade, Transaction

# The admin page is where we can see backend data and make changes in a nice, easy to use GUI
# This registers the Post object, which must first be impiorted as
admin.site.register(Post)
admin.site.register(Game)
admin.site.register(Trade)
admin.site.register(Transaction)
