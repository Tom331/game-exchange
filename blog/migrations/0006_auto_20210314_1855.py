# Generated by Django 3.1.7 on 2021-03-14 18:55

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20210314_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='game_c',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 14, 18, 55, 21, 815477, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='post',
            name='date_posted',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 14, 18, 55, 21, 815172, tzinfo=utc)),
        ),
    ]
