# Generated by Django 3.1.7 on 2021-04-29 05:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0015_auto_20210424_2139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='condition',
            field=models.CharField(choices=[('Bad - A lot of scratches, but still works', 'Bad - A lot of scratches, but still works'), ('OK - 1 or 2 small scratches', 'OK - 1 or 2 small scratches'), ('Good - No scratches, 1 or 2 smudges', 'Good - No scratches, 1 or 2 smudges'), ('Perfect - No scratches or smudges', 'Perfect - No scratches or smudges')], max_length=50),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 1, 22, 40, 40, 435399)),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='open_expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 7, 22, 40, 40, 435416)),
        ),
    ]