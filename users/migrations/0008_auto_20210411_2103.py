# Generated by Django 3.1.7 on 2021-04-12 04:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20210411_1048'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='email_confirmation_due_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 18, 21, 3, 45, 579758)),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='key_expires',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 18, 21, 3, 45, 579704)),
        ),
    ]
