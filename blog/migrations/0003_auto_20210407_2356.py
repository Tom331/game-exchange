# Generated by Django 3.1.7 on 2021-04-08 06:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20210405_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 10, 23, 54, 20, 736590)),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='open_expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 16, 23, 54, 20, 736607)),
        ),
    ]
