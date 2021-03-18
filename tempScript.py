from blog.models import Game
import csv
from django.contrib.auth.models import User

with open('../resources/Game_Datasets/PS4-2.csv') as f:
    admin = User.objects.filter(username='admin').first()
    reader = csv.reader(f)
    for row in reader:
        _, created = Game.objects.get_or_create(
            #todo: add id ref since we have to maintain the pk
            name=row[1],
            platform=row[2],
            author=admin,
        )


