# Generated by Django 3.1.7 on 2021-04-04 22:05

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('platform', models.CharField(max_length=100)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('name_and_platform', models.TextField(default='N/A')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_trade_proposed', models.BooleanField(default=False)),
                ('desired_game', models.ForeignKey(db_column='desired_game', on_delete=django.db.models.deletion.CASCADE, related_name='desired_game', to='blog.game')),
                ('owned_game', models.ForeignKey(db_column='owned_game', on_delete=django.db.models.deletion.CASCADE, related_name='owned_game', to='blog.game')),
                ('user_who_posted', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.TextField()),
                ('expiry_date', models.DateTimeField(default=datetime.datetime(2021, 4, 7, 15, 5, 15, 936507))),
                ('open_expiry_date', models.DateTimeField(default=datetime.datetime(2021, 4, 13, 15, 5, 15, 936531))),
                ('user_cancelled_date', models.DateTimeField(blank=True, null=True)),
                ('trade_one', models.ForeignKey(db_column='trade_one', on_delete=django.db.models.deletion.CASCADE, related_name='trade_one', to='blog.trade')),
                ('trade_two', models.ForeignKey(db_column='trade_two', on_delete=django.db.models.deletion.CASCADE, related_name='trade_two', to='blog.trade')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('date_posted', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
