from django.db import models

print('~~~top of chat/models.py~~~')


from django.conf import settings
User = settings.AUTH_USER_MODEL
# from django.contrib.auth import get_user_model
# User = get_user_model()
# from users.models import User

from django.utils import timezone
from blog.models import Transaction


class Message(models.Model):
    author = models.ForeignKey(User, related_name='author_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now) #todo: timezone fix?
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    def __str__(self):
        return self.author.username

    def last_10_messages(self, transaction_id):
        return Message.objects.filter(transaction_id=transaction_id).order_by('-timestamp').all()[:10] # only load last x msgs from DB

print('~~~bottom of chat/models.py~~~')
