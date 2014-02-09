from __future__ import print_function, unicode_literals

import sys
from collections import defaultdict

from django.conf import settings

import tvdbpy
from qsaui.models import Series, Episode


class InvalidUpdateKind(Exception):
    """The given update.kind is not valid."""


class CatalogueUpdater(object):

    def __init__(self, stdout=sys.stdout):
        super(CatalogueUpdater, self).__init__()
        self.stdout = stdout

    def update(self, period=tvdbpy.TvDB.WEEK):
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

    def _update_item(self, update, item_class):
        new = ''
        tvdb_item = None

        try:
            item = item_class.objects.get(tvdb_id=update.id)
        except item_class.DoesNotExist:
            item = None

        series = None
        if update.kind == tvdbpy.TvDB.EPISODE:
            try:  # may be a new Episode!
                series = Series.objects.get(tvdb_id=update.series)
            except Series.DoesNotExist:
                return

        # the series exists in our DB but the episode does not -- new episode
        if item is None and series is not None:
            tvdb_item = update.get_updated_item()
            item = Episode.objects.create(
                tvdb_id=tvdb_item.id, series=series, season=tvdb_item.season,
                number=tvdb_item.number)
            new = 'new episode '

        if (item is not None and item.last_updated is not None and
                item.last_updated < update.timestamp):
            # item needs update
            if tvdb_item is None:
                tvdb_item = update.get_updated_item()

            item_name = unicode(item)
            if series is not None:
                item_name = '%s %s' % (series.name, item_name)

            update_time = update.timestamp.isoformat()
            self.stdout.write(
                '%s"%s" (update from %s)\n' % (new, item_name, update_time))
            item.update_from_tvdb(tvdb_item=tvdb_item, extended=False)

            return item

    def update_series(self, update):
        return self._update_item(update, Series)

    def update_episode(self, update):
        return self._update_item(update, Episode)
