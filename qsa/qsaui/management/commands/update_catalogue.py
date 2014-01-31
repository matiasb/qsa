from __future__ import unicode_literals

from collections import defaultdict
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

import tvdbpy
from qsaui.models import Series, Episode


class Command(BaseCommand):

    help = 'Update all the series that changed in the last week.'

    def handle(self, *args, **options):
        updated = defaultdict(list)
        unknown = defaultdict(int)

        client = tvdbpy.TvDB(settings.TVDBPY_API_KEY)
        updates = client.updated(timeframe=tvdbpy.TvDB.WEEK)
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
                self.stderr.write('Invalid update kind: %s' % kind)
                continue

            if result:
                updated[kind].append(result.name)
            else:
                unknown[kind] += 1

        if unknown:
            stats = ' and '.join(
                '%s %s' % (v, k) for (k, v) in unknown.iteritems())
            self.stderr.write(
                'There were %s that do not exist locally.' % stats)

        if updated:
            msg = 'Successfully updated %s' % ' and '.join(
                '%s %s' % (len(v), k) for k, v in updated.iteritems())
        else:
            msg = 'Nothing to update.'
        self.stdout.write(msg)

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
            new = 'new %s episode ' % series.name

        if (item is not None and item.last_updated is not None and
                item.last_updated < update.timestamp):
            # item needs update
            if tvdb_item is None:
                tvdb_item = update.get_updated_item()

            item_name = unicode(item)
            if series is not None:
                item_name = '%s %s' % (series.name, item_name)

            update_time = update.timestamp.isoformat()
            msg = 'Processing %s"%s" (update from %s)...'
            self.stdout.write(
                msg % (new, item_name, update_time), ending='')
            item.update_from_tvdb(tvdb_item=tvdb_item, extended=False)
            self.stdout.write(' [OK]')

        return item

    def update_series(self, update):
        return self._update_item(update, Series)

    def update_episode(self, update):
        return self._update_item(update, Episode)
