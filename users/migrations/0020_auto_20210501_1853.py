# Generated by Django 3.1.7 on 2021-05-02 01:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_auto_20210430_1656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='email_confirmation_due_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 8, 18, 53, 1, 588193)),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='key_expires',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 8, 18, 53, 1, 588169)),
        ),
    ]