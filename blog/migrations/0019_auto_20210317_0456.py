# Generated by Django 3.1.7 on 2021-03-17 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0018_auto_20210317_0433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='name_and_platform',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='game',
            name='platform',
            field=models.CharField(max_length=100),
        ),
    ]
