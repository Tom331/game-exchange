# Generated by Django 3.1.7 on 2021-03-28 18:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_auto_20210327_0129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 31, 11, 48, 57, 403615)),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='open_expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 6, 11, 48, 57, 403632)),
        ),
    ]
