from __future__ import unicode_literals

try:
    from urllib.parse import urlencode, quote
except ImportError:
    from urllib import urlencode, quote

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

import tvdbpy


GOOGLE = 'google.com'
KICKASS = 'kickass.so'
ISOHUNT = 'isohunt.to'
PIRATE_BAY = 'thepiratebay.se'


class BaseTvDBItem(models.Model):

    name = models.TextField()
    overview = models.TextField()
    first_aired = models.DateField(null=True)
    rating = models.FloatField(null=True)
    rating_count = models.PositiveIntegerField(null=True)
    tvdb_id = models.CharField(max_length=256, unique=True)
    imdb_id = models.CharField(max_length=256)

    last_updated = models.DateTimeField(null=True)

    class Meta:
        abstract = True

    @property
    def imdb_url(self):
        if self.imdb_id:
            return 'http://www.imdb.com/title/%s/' % self.imdb_id

    def _update_text_attrs(self, attrs, tvdb_item):
        for attr in attrs:
            value = getattr(tvdb_item, attr)
            if value is None:
                value = ''
            setattr(self, attr, value)

    def update_from_tvdb(self, tvdb_item):
        self._update_text_attrs(('name', 'overview', 'imdb_id'), tvdb_item)

        self.first_aired = tvdb_item.first_aired
        self.rating = tvdb_item.rating
        self.rating_count = tvdb_item.rating_count

        self.last_updated = datetime.utcnow()
        self.save()


class SeriesManager(models.Manager):

    def get_or_create(self, *args, **kwargs):
        extended = kwargs.pop('extended', False)

        instance, created = super(
            SeriesManager, self).get_or_create(*args, **kwargs)
        if created:
            instance.update_from_tvdb(extended=extended)

        return instance, created


class Series(BaseTvDBItem):

    objects = SeriesManager()

    runtime = models.PositiveIntegerField(null=True)  # minutes
    network = models.TextField()
    tags = models.TextField()
    cast = models.TextField()
    poster = models.URLField()
    banner = models.URLField()
    completed = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'series'

    def __str__(self):
        return self.name

    def seasons(self, with_specials=False):
        episodes = self.episode_set
        if not with_specials:
            episodes = episodes.exclude(season=0)
        seasons = episodes.distinct().values_list('season', flat=True)
        return seasons.order_by('season')

    @property
    def next_episode(self):
        episodes = self.episode_set.filter(first_aired__gt=datetime.utcnow())
        if episodes.exists():
            return episodes.order_by('first_aired', 'number')[0]

    @property
    def last_episode(self):
        episodes = self.episode_set.filter(first_aired__lte=datetime.utcnow())
        if episodes.exists():
            return episodes.order_by('-first_aired', '-number')[0]

    def update_from_tvdb(self, tvdb_item=None, extended=True):
        """Update this instance using the remote info from TvDB site."""
        if tvdb_item is None:
            client = tvdbpy.TvDB(settings.TVDBPY_API_KEY)
            tvdb_item = client.get_series_by_id(
                self.tvdb_id, extended=extended)

        self._update_text_attrs(
            ('runtime',  'network', 'poster', 'banner'), tvdb_item)

        self.cast = ', '.join(tvdb_item.actors)
        self.tags = ', '.join(tvdb_item.genre)

        self.completed = (tvdb_item.status.lower() == 'ended')

        super(Series, self).update_from_tvdb(tvdb_item)

        if extended:
            # load seasons, which are already fetched
            self._fetch_episodes(tvdb_item)

    def _fetch_episodes(self, tvdb_item):
        for season, episodes in tvdb_item.seasons.items():
            for i, e in episodes.items():
                episode, _ = Episode.objects.get_or_create(
                    series=self, season=season, number=i)
                episode.tvdb_id = e.id
                episode.update_from_tvdb(tvdb_item=e)


class Episode(BaseTvDBItem):

    series = models.ForeignKey(Series)
    season = models.PositiveIntegerField()
    number = models.PositiveIntegerField()
    image = models.URLField()
    guest_stars = models.TextField(null=True)
    writers = models.TextField(null=True)
    director = models.TextField(null=True)

    class Meta:
        unique_together = ('series', 'season', 'number')

    def __str__(self):
        return '%s %s' % (self.series.name, self.short_name)

    def update_from_tvdb(self, tvdb_item, extended=False):
        self.season = tvdb_item.season
        self.number = tvdb_item.number

        self._update_text_attrs(('director', 'image'), tvdb_item)

        for attr in ('guest_stars', 'writers'):
            value = getattr(tvdb_item, attr)
            if value:
                setattr(self, attr, ', '.join(value))

        super(Episode, self).update_from_tvdb(tvdb_item)

    @property
    def already_aired(self):
        return self.first_aired < datetime.utcnow().date()

    @property
    def isohunt_torrent_url(self):
        params = {
            'ihq': str(self),
            'Torrent_sort': 'seeders.desc',
        }
        return 'http://isohunt.to/torrents/?' + urlencode(params)

    @property
    def kickass_torrent_url(self):
        search_term = quote(str(self))
        url = 'https://kickass.so/usearch/%s/?field=seeders&sorder=desc'
        return url % search_term

    @property
    def piratebay_torrent_url(self):
        search_term = quote(str(self))
        return 'http://thepiratebay.se/search/%s/0/7/0' % search_term

    @property
    def search_torrent_url(self):
        search_term = quote('%s torrent' % str(self))
        return 'https://www.google.com/search?q=' + search_term

    @property
    def torrent_urls(self):
        return [
            (ISOHUNT, self.isohunt_torrent_url),
            (KICKASS, self.kickass_torrent_url),
            (PIRATE_BAY, self.piratebay_torrent_url),
            (GOOGLE, self.search_torrent_url),
        ]

    @property
    def short_name(self):
        return 'S%02dE%02d' % (self.season, self.number)


class Watcher(models.Model):
    user = models.OneToOneField(User)
    series = models.ManyToManyField(Series)

    def episodes_from_yesterday(self):
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        return Episode.objects.filter(
            series__in=self.series.all(),
            first_aired=yesterday).order_by('name')

    def episodes_for_next_week(self):
        today = datetime.utcnow().date()
        a_week_from_now = today + timedelta(weeks=1)
        return Episode.objects.filter(
            series__in=self.series.all(),
            first_aired__range=(today, a_week_from_now)).order_by(
            'first_aired', 'name')

    def episodes_coming_soon(self):
        today = datetime.utcnow().date()
        return Episode.objects.filter(
            series__in=self.series.all(),
            first_aired__gte=today).order_by('first_aired', 'name')

    def episodes_from_last_week(self):
        today = datetime.utcnow().date()
        a_week_ago = today - timedelta(weeks=1)
        day_before_yesterday = today - timedelta(days=2)
        return Episode.objects.filter(
            series__in=self.series.all(),
            first_aired__range=(a_week_ago, day_before_yesterday)).order_by(
            '-first_aired', 'name')


def create_watcher(sender, instance, created, raw, **kwargs):
    assert sender == User
    if created and not raw:
        Watcher.objects.create(user=instance)


models.signals.post_save.connect(
    create_watcher, sender=User, dispatch_uid='create_watcher_from_user')
