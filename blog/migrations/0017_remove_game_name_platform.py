# Generated by Django 3.1.7 on 2021-03-17 04:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0016_game_name_platform'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='name_platform',
        ),
    ]