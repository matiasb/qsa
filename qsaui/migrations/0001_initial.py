# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.TextField()),
                ('overview', models.TextField()),
                ('first_aired', models.DateField(null=True)),
                ('rating', models.FloatField(null=True)),
                ('rating_count', models.PositiveIntegerField(null=True)),
                ('tvdb_id', models.CharField(unique=True, max_length=256)),
                ('imdb_id', models.CharField(max_length=256)),
                ('last_updated', models.DateTimeField(null=True)),
                ('season', models.PositiveIntegerField()),
                ('number', models.PositiveIntegerField()),
                ('image', models.URLField()),
                ('guest_stars', models.TextField(null=True)),
                ('writers', models.TextField(null=True)),
                ('director', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.TextField()),
                ('overview', models.TextField()),
                ('first_aired', models.DateField(null=True)),
                ('rating', models.FloatField(null=True)),
                ('rating_count', models.PositiveIntegerField(null=True)),
                ('tvdb_id', models.CharField(unique=True, max_length=256)),
                ('imdb_id', models.CharField(max_length=256)),
                ('last_updated', models.DateTimeField(null=True)),
                ('runtime', models.PositiveIntegerField(null=True)),
                ('network', models.TextField()),
                ('tags', models.TextField()),
                ('cast', models.TextField()),
                ('poster', models.URLField()),
                ('banner', models.URLField()),
                ('completed', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'series',
            },
        ),
        migrations.CreateModel(
            name='Watcher',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('series', models.ManyToManyField(to='qsaui.Series')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='episode',
            name='series',
            field=models.ForeignKey(to='qsaui.Series'),
        ),
        migrations.AlterUniqueTogether(
            name='episode',
            unique_together=set([('series', 'season', 'number')]),
        ),
    ]
