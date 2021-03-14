from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime # timezone takes timezone into consideration (even though it doesn't seem to)

# we're inheriting from the models.Model
# https://docs.djangoproject.com/en/3.1/topics/db/models/
class Post(models.Model):
    title = models.CharField(max_length=100) # character field
    content = models.TextField() # Unrestricted text
    date_posted = models.DateTimeField(default=timezone.now)
    last_modified = models.DateTimeField(auto_now=True)

    # author is a one-to-many relationship which uses a foreign key
    # the argument to ForeignKey is the related table
    # on_delete tells django to delete all posts by a user when that user is deleted
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # Convenience method to print out the title of a Post
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class Game_c(models.Model):
    name = models.TextField() # Unrestricted text
    platform = models.CharField(max_length=100) # character field
    created_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name # return game name when game.objects.all() is called

