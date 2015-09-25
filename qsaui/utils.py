from __future__ import print_function, unicode_literals

import sys
from collections import defaultdict

import tvdbpy
from django.conf import settings

from qsaui.models import Series, Episode


class InvalidUpdateKind(Exception):
    """The given update.kind is not valid."""


class CatalogueUpdater(object):

    def __init__(self, stdout=sys.stdout):
        super(CatalogueUpdater, self).__init__()
        self.stdout = stdout

    def update(self, period=tvdbpy.TvDB.WEEK):
        if period == tvdbpy.TvDB.ALL:
            return self.update_all_series()
        else:
            return self.update_from_period(period)

    def update_all_series(self):
        updated = []
        for series in Series.objects.all():
            series.update_from_tvdb(extended=True)
            updated.append(series.name)
            self.stdout.write('"%s"\n' % series.name)

        return {tvdbpy.TvDB.SERIES: updated}, {}

    def update_from_period(self, period):
        updated = defaultdict(list)
        unknown = defaultdict(int)

        client = tvdbpy.TvDB(settings.TVDBPY_API_KEY)
        updates = client.updated(timeframe=period)
        for update in updates:
            result = None
            kind = update.kind
            if kind == tvdbpy.TvDB.SERIES:
                result = self.update_series(update)
            elif kind == tvdbpy.TvDB.EPISODE:
                result = self.update_episode(update)
            elif kind == tvdbpy.TvDB.BANNER:
                continue
            else:
                raise InvalidUpdateKind(kind)

            if result:
                updated[kind].append(result.name)
            else:
                unknown[kind] += 1

        return updated, unknown

    def _update_item(self, update, item, created=False):
        assert item is not None
        if item.last_updated is None or item.last_updated < update.timestamp:
            # item needs update
            tvdb_item = update.get_updated_item()
            item.update_from_tvdb(tvdb_item=tvdb_item, extended=False)

            update_time = update.timestamp.isoformat()
            new = 'New ' if created else ''
            self.stdout.write(
                '%s"%s" (update from %s)\n' % (new, item, update_time))

            return item

    def update_series(self, update):
        try:
            series = Series.objects.get(tvdb_id=update.id)
        except Series.DoesNotExist:
            return

        return self._update_item(update, series)

    def update_episode(self, update):
        try:  # process this episode only if we know the series linked to it
            series = Series.objects.get(tvdb_id=update.series)
        except Series.DoesNotExist:
            return

        episode, created = Episode.objects.get_or_create(
            series=series, tvdb_id=update.id,
            defaults=dict(season=0, number=0))

        return self._update_item(update, episode, created)
