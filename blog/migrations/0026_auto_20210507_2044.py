# Generated by Django 3.1.7 on 2021-05-08 03:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0025_auto_20210507_1116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 10, 20, 44, 52, 105875)),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='open_expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 16, 20, 44, 52, 105893)),
        ),
    ]