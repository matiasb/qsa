from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

import tvdbpy


class Series(models.Model):

    name = models.TextField()
    overview = models.TextField()
    first_aired = models.DateField(null=True)
    runtime = models.PositiveIntegerField(null=True)  # minutes
    tags = models.TextField()
    cast = models.TextField()
    poster = models.URLField()
    completed = models.BooleanField(default=False)
    tvdb_id = models.CharField(max_length=256)
    imdb_id = models.CharField(max_length=256)

    def update_from_tvdb(self):
        """Update this instance using the remote info from TvDB site."""
        client = tvdbpy.TvDB(settings.TVDBPY_API_KEY)
        series = client.get_series_by_id(self.tvdb_id)
        attrs = (
            'name', 'overview', 'first_aired', 'runtime',  # 'tags', 'cast',
            'poster', 'imdb_id',
        )
        for attr in attrs:
            setattr(self, attr, getattr(series, attr))
        self.completed = (series.status.lower() == 'ended')
        self.save()


class Season(models.Model):

    series = models.ForeignKey(Series)
    year = models.PositiveIntegerField(null=True)
    number = models.PositiveIntegerField()


class Episode(models.Model):

    season = models.ForeignKey(Season)
    number = models.PositiveIntegerField()
    name = models.TextField()
    overview = models.TextField()
    first_aired = models.DateField()
    image = models.URLField()
    tvdb_id = models.CharField(max_length=256)
    imdb_id = models.CharField(max_length=256)
    writer = models.TextField(null=True)
    director = models.TextField(null=True)


class Watcher(models.Model):
    user = models.OneToOneField(User)
    series = models.ManyToManyField(Series)


def create_watcher(sender, instance, created, **kwargs):
    assert sender == User
    if created:
        Watcher.objects.create(user=instance)


models.signals.post_save.connect(
    create_watcher, sender=User, dispatch_uid='create_watcher_from_user')
