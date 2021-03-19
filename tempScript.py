from blog.models import Game
import csv
from django.contrib.auth.models import User

with open('zResources-ignore/Mar-19-12am-Sony.csv') as f:
    admin = User.objects.filter(username='admin').first()
    reader = csv.reader(f)
    for row in reader:
        _, created = Game.objects.get_or_create(
            id=row[0],
            name=row[1],
            platform=row[2],
            author=admin,
        )
