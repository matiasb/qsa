from __future__ import unicode_literals
from __future__ import print_function

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

import tvdbpy


class SeriesManager(models.Manager):

    def get_or_create(self, *args, **kwargs):
        extended = kwargs.pop('extended', False)

        instance, created = super(
            SeriesManager, self).get_or_create(*args, **kwargs)
        if created:
            instance.update_from_tvdb(extended=extended)

        return instance, created


class Series(models.Model):

    objects = SeriesManager()

    name = models.TextField()
    overview = models.TextField()
    first_aired = models.DateField(null=True)
    runtime = models.PositiveIntegerField(null=True)  # minutes
    network = models.TextField()
    tags = models.TextField()
    cast = models.TextField()
    poster = models.URLField()
    banner = models.URLField()
    completed = models.BooleanField(default=False)
    tvdb_id = models.CharField(max_length=256)
    imdb_id = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name

    def update_from_tvdb(self, extended=False):
        """Update this instance using the remote info from TvDB site."""
        client = tvdbpy.TvDB(settings.TVDBPY_API_KEY)
        tvdb_series = client.get_series_by_id(self.tvdb_id)
        attrs = (
            'name', 'overview', 'first_aired', 'runtime',  'network',
            'poster', 'banner', 'imdb_id',
        )
        for attr in attrs:
            setattr(self, attr, getattr(tvdb_series, attr))

        self.cast = ', '.join(tvdb_series.actors)
        self.tags = ', '.join(tvdb_series.genre)

        self.completed = (tvdb_series.status.lower() == 'ended')

        if extended:
            # grab series.seasons
            self._fetch_episodes(tvdb_series)

        self.save()

    def _fetch_episodes(self, tvdb_series):
        for season, episodes in tvdb_series.seasons.iteritems():
            for i, e in episodes.iteritems():
                episode, _ = Episode.objects.get_or_create(
                    series=self, season=season, number=i, tvdb_id=e.id)
                episode.update_from_tvdb(e)


class Episode(models.Model):

    series = models.ForeignKey(Series)
    season = models.PositiveIntegerField()
    number = models.PositiveIntegerField()
    name = models.TextField()
    overview = models.TextField()
    first_aired = models.DateField(null=True)
    image = models.URLField()
    tvdb_id = models.CharField(max_length=256)
    imdb_id = models.CharField(max_length=256)
    guest_stars = models.TextField(null=True)
    writer = models.TextField(null=True)
    director = models.TextField(null=True)

    class Meta:
        unique_together = ('series', 'season', 'number')

    def __unicode__(self):
        if self.season > 0:
            season = 'season %s' % self.season
        else:
            season = 'specials'
        return '%s S%.2fE%.2fs' % (self.series.name, season, self.number)

    def _blank_if_none(self, attr, value):
        if value is None:
            value = ''
        setattr(self, attr, value)

    def update_from_tvdb(self, tvdb_episode):
        attrs = (
            'director', 'guest_stars', 'image', 'name', 'overview', 'writer',
        )
        for attr in attrs:
            self._blank_if_none(attr, getattr(tvdb_episode, attr))
        self.first_aired = tvdb_episode.first_aired
        self.save()


class Watcher(models.Model):
    user = models.OneToOneField(User)
    series = models.ManyToManyField(Series)


def create_watcher(sender, instance, created, **kwargs):
    assert sender == User
    if created:
        Watcher.objects.create(user=instance)


models.signals.post_save.connect(
    create_watcher, sender=User, dispatch_uid='create_watcher_from_user')
