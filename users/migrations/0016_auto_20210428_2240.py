# Generated by Django 3.1.7 on 2021-04-29 05:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20210424_2139'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='confirmed_trade_email_opt_in',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='email_confirmation_due_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 5, 22, 40, 40, 454616)),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='key_expires',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 5, 22, 40, 40, 454600)),
        ),
    ]
