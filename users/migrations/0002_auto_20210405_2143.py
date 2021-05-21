# Generated by Django 3.1.7 on 2021-04-06 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='lat',
            field=models.DecimalField(blank=True, decimal_places=11, default=None, max_digits=14, null=True),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='long',
            field=models.DecimalField(blank=True, decimal_places=11, default=None, max_digits=14, null=True),
        ),
    ]