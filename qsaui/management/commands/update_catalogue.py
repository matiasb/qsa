from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from qsaui.utils import CatalogueUpdater


class Command(BaseCommand):

    help = 'Update all the series that changed in the last week.'

    def handle(self, *args, **options):
        updated, unknown = CatalogueUpdater(stdout=self.stdout).update()

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
