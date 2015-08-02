from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError

from tvdbpy import TvDB

from qsaui.utils import CatalogueUpdater


class Command(BaseCommand):

    periods = [TvDB.DAY, TvDB.WEEK, TvDB.MONTH, TvDB.ALL]
    args = '[%s]' % '|'.join(periods)
    help = 'Update all the series that changed in the last week.'

    def handle(self, *args, **options):
        try:
            period = args[0]
        except IndexError:
            period = TvDB.WEEK

        if period not in self.periods:
            raise CommandError(
                'Invalid period %r, should be one of %s' % (period, self.args))

        updated, unknown = CatalogueUpdater(stdout=self.stdout).update(
            period=period)

        if unknown:
            stats = ' and '.join(
                '%s %s' % (v, k) for (k, v) in unknown.items())
            self.stderr.write(
                'There were %s that do not exist locally.' % stats)

        if updated:
            msg = 'Successfully updated %s' % ' and '.join(
                '%s %s' % (len(v), k) for k, v in updated.items())
        else:
            msg = 'Nothing to update.'
        self.stdout.write(msg)
