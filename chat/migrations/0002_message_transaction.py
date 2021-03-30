# Generated by Django 3.1.7 on 2021-03-27 08:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_auto_20210327_0129'),
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='transaction',
            field=models.ForeignKey(default=127, on_delete=django.db.models.deletion.CASCADE, to='blog.transaction'),
            preserve_default=False,
        ),
    ]