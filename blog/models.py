
print('~~~\n\nvery top in blog/models.py\n\n~~~')

from django.db import models
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, timedelta

from django.conf import settings
User = settings.AUTH_USER_MODEL

# from django.contrib.auth import get_user_model
# User = get_user_model()

# from users.models import User


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
    name_and_platform = models.TextField(default='N/A', unique=True)

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
    CONDITION_CHOICES = (
        ('OK - A lot of scratches, but still works', 'OK - A lot of scratches, but still works'),
        ('Fair - 1 or 2 small scratches', 'Fair - 1 or 2 small scratches'),
        ('Good - No scratches, 1 or 2 smudges', 'Good - No scratches, 1 or 2 smudges'),
        ('Perfect - No scratches or smudges', 'Perfect - No scratches or smudges'),
    )

    name = models.TextField() # Unrestricted text
    created_date = models.DateTimeField(default=timezone.now)
    is_trade_proposed = models.BooleanField(default=False) # lock the Trade so other users can't match with it

    # Ignore the trade when querying on Your Trades page and on trade insertion
    # is_trade_proposed is left as true, which takes care of Matches page. If "Flagged as incomplete", is_completed set to true
    is_completed = models.BooleanField(default=False)

    # The user who originally submitted the trade. They can delete the trade record. If their user is deleted, so is the trade
    user_who_posted = models.ForeignKey(User, on_delete=models.CASCADE)

    # The owned game of the user who created the Trade record. If a game is deleted, so is the trade
    # Specify the related_name to avoid the same lookup name (Trade.Game)
    owned_game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='owned_game', db_column='owned_game', null=True, blank=True)
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES, null=True, blank=True) # Disc condition of owned game

    # The desired game of the user who created the Trade record
    # Specify the related_name to avoid the same lookup name (Trade.Game)
    desired_game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='desired_game', db_column='desired_game', null=True, blank=True)

    # The highest dollar value the user is willing to buy desired_game for
    buy_price = models.IntegerField(default=None, null=True, blank=True)

    # The lowest dollar value the user is willing to sell owned_game for
    sell_price = models.IntegerField(default=None, null=True, blank=True)

    # Holds the calculated Average for buy_price and sell_price between the 2 matched Trades, which will be the price set on the created transaction.
    transaction_price = models.IntegerField(default=None, null=True, blank=True)


    def get_trade_name(self):
        return ''.join([self.user_who_posted.username, '(', timezone.now().strftime("%b %d, %Y %H:%M:%S UTC"), ')'])

    def get_condition_choices(self):
        return self.CONDITION_CHOICES

    def save(self, *args, **kwargs):
        self.name = self.get_trade_name()
        super(Trade, self).save(*args, **kwargs)

    def __str__(self):
        return self.name # return game name when game.objects.all() is called


class Transaction(models.Model):
    name = models.TextField() # Unrestricted text
    created_date = models.DateTimeField(default=timezone.now)

    # The trade of the user who created the Transaction record (1st to confirm)
    # Specify the related_name to avoid the same lookup name (Trade.Game)
    trade_one = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name='trade_one', db_column='trade_one')

    # The trade of the user who was the 2nd to confirm
    # Specify the related_name to avoid the same lookup name (Trade.Game)
    trade_two = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name='trade_two', db_column='trade_two')

    # Options: Cancelled: cancelled by user, Cancelled: auto-cancelled due to inactivity for 2 days, Open
    status = models.TextField() # Unrestricted text. Validated in form.

    # While the trade is in "Waiting on user..." status, if trade_two.user does not confirm the trade within 3 days, it will be auto-cancelled
    expiry_date = models.DateTimeField(default=datetime.today() + timedelta(days=3))

    # While the trade is in "Open" status, if the trade does not complete within 9 days after the transaction was created, it will be auto-cancelled
    open_expiry_date = models.DateTimeField(default=datetime.today() + timedelta(days=9))

    user_cancelled_date = models.DateTimeField(null=True, blank=True) # Date the user cancelled the transaction

    # The duration between the first user confirming the trade, and completion by both users
    confirmed_to_completed_duration = models.DurationField(null=True, blank=True)

    # The first user to complete the trade. When querying transactions on the matches page for Confirmed Trades limit,
    # ignore transactions where current_user = user_who_completed OR where status = 'Completed by both users'
    user_who_completed = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # If this is a buy/sell transaction, this is the FLOOR of the AVERAGE of the sell price and buy price of related trades
    price = models.IntegerField(default=None, null=True, blank=True)

    def get_transaction_name(self):
        return ''.join([str(self.trade_one_id), ' and ', str(self.trade_two_id), ' on ', timezone.now().strftime("%b %d, %Y %H:%M:%S UTC"), ''])

    def get_status_on_insert(self):
        if len(str(self.trade_two.user_who_posted)) > 25:
            return 'Waiting for 2nd confirmation from ' + str(self.trade_two.user_who_posted)[:25] + '...'
        else:
            return 'Waiting for 2nd confirmation from ' + str(self.trade_two.user_who_posted)

    def save(self, *args, **kwargs):
        if self.name == '':
            self.name  = self.get_transaction_name()
        if self.status == '':
            self.status = self.get_status_on_insert()
        super(Transaction, self).save(*args, **kwargs)

    def __str__(self):
        return self.name # return name when game.objects.all() is called

    def get_absolute_url(self): #todo: remove?
        return reverse('confirmed-trade', kwargs={'pk': self.pk})

print('~~~bottom of blog/models.py~~~')