# Generated by Django 3.1.7 on 2021-05-02 02:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_auto_20210501_1853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='email_confirmation_due_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 8, 19, 41, 13, 982366)),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='key_expires',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 8, 19, 41, 13, 982345)),
        ),
    ]
