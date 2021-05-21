# Generated by Django 3.1.7 on 2021-04-11 17:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20210411_0041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='activation_key',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='key_expires',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 19, 10, 48, 57, 66409)),
        ),
    ]
