# Generated by Django 3.1.7 on 2021-05-07 18:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0024_auto_20210507_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='condition',
            field=models.CharField(blank=True, choices=[('Bad - A lot of scratches, but still works', 'Bad - A lot of scratches, but still works'), ('OK - 1 or 2 small scratches', 'OK - 1 or 2 small scratches'), ('Good - No scratches, 1 or 2 smudges', 'Good - No scratches, 1 or 2 smudges'), ('Perfect - No scratches or smudges', 'Perfect - No scratches or smudges')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 10, 11, 16, 22, 36277)),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='open_expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 16, 11, 16, 22, 36294)),
        ),
    ]
