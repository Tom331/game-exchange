from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

# we're inheriting from the models.Model
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


class Game(models.Model):
    name = models.TextField()  # Unrestricted text
    platform = models.CharField(max_length=100)  # character field
    created_date = models.DateTimeField(default=timezone.now)
    name_and_platform = models.TextField(default='N/A') #todo: find a good max char limit

    # ForeignKey represents a many to one relationship.
    # if user is deleted, all Game records they made are deleted
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name  # return game name when game.objects.all() is called

    def get_name_and_platform(self):
        return ''.join([self.name, '(', self.platform, ')'])

    def save(self, *args, **kwargs):
        self.name_and_platform = self.get_name_and_platform()
        super(Game, self).save(*args, **kwargs)




class Trade(models.Model):
    name = models.TextField() # Unrestricted text
    created_date = models.DateTimeField(default=timezone.now)
    is_trade_proposed = models.BooleanField(default=False) # lock the Trade so other users can't match with it

    # The user who originally submitted the trade. They can delete the trade record. If their user is deleted, so is the trade
    user_who_posted = models.ForeignKey(User, on_delete=models.CASCADE)

    # The owned game of the user who created the Trade record. If a game is deleted, so is the trade
    # Specify the related_name to avoid the same lookup name (Trade.Game)
    owned_game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='owned_game', db_column='owned_game')

    # The desired game of the user who created the Trade record
    # Specify the related_name to avoid the same lookup name (Trade.Game)
    desired_game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='desired_game', db_column='desired_game')

    def get_trade_name(self):
        return ''.join([self.user_who_posted.username, '(', timezone.now().strftime("%b %d, %Y %H:%M:%S UTC"), ')'])

    def save(self, *args, **kwargs):
        self.name = self.get_trade_name()
        super(Trade, self).save(*args, **kwargs)

    def __str__(self):
        return self.name # return game name when game.objects.all() is called


class Transaction(models.Model):
    name = models.TextField() # Unrestricted text
    created_date = models.DateTimeField(default=timezone.now)

    # The owned game of the user who created the Trade record. If a game is deleted, so is the trade
    # Specify the related_name to avoid the same lookup name (Trade.Game)
    trade_one = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name='trade_one', db_column='trade_one')

    # The desired game of the user who created the Trade record
    # Specify the related_name to avoid the same lookup name (Trade.Game)
    trade_two = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name='trade_two', db_column='trade_two')

    # def get_trade_name(self):
    #     return ''.join([self.user_who_posted.username, '(', timezone.now().strftime("%b %d, %Y %H:%M:%S UTC"), ')'])
    #
    # def save(self, *args, **kwargs):
    #     print('trade_one username: ' + str(self.trade_one.user.username))
    #     print('trade_two username: ' + str(self.trade_two.user.username))
    #     self.name = self.get_trade_name()
    #     super(Trade, self).save(*args, **kwargs)

    def __str__(self):
        return self.name # return game name when game.objects.all() is called

