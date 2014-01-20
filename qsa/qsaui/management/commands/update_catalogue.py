from __future__ import unicode_literals

import time
from collections import defaultdict
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

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

        self.stdout.write(
            'Successfully updated %s' %
            ' and '.join('%s %s' % (len(v), k) for k, v in updated.iteritems())
        )

    def _process_item(self, tvdb_item, item, new=False):
        if new:
            new = 'new item '
        else:
            new = ''
        self.stdout.write('Processing %s"%s"...' % (new, item), ending='')
        item.update_from_tvdb(tvdb_item=tvdb_item, extended=False)
        self.stdout.write(' [OK]')
        return item

    def _update_item(self, update, item_class):
        try:
            item = item_class.objects.get(tvdb_id=update.id)
        except item_class.DoesNotExist:
            return

        if (item.last_updated is not None and
                item.last_updated > update.timestamp):
            return

        return self._process_item(update.get_updated_item(), item)

    def update_series(self, update):
        return self._update_item(update, Series)

    def update_episode(self, update):
        episode = self._update_item(update, Episode)
        if episode is None:
            try:
                series = Series.objects.get(tvdb_id=update.series)
            except Series.DoesNotExist:
                return

            tvdb_item = update.get_updated_item()
            episode, created = Episode.objects.get_or_create(
                tvdb_id=tvdb_item.id, series=series, season=tvdb_item.season,
                number=tvdb_item.number)
            self._process_item(tvdb_item, episode, new=True)

        return episode
