# Generated by Django 3.1.7 on 2021-04-06 04:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 8, 21, 43, 45, 880292)),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='open_expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 14, 21, 43, 45, 880311)),
        ),
    ]
