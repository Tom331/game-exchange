# Generated by Django 3.1.7 on 2021-03-17 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0021_auto_20210317_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='name_and_platform',
            field=models.TextField(default='N/A'),
        ),
    ]