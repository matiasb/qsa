from StringIO import StringIO

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import linebreaksbr
from django.template.response import TemplateResponse
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
)
from tvdbpy import TvDB

from qsaui.forms import UpdateCatalogueForm
from qsaui.models import Series, Episode
from qsaui.utils import CatalogueUpdater


@require_GET
@login_required
def home(request):
    watcher = request.user.watcher
    context = dict(
        yesterday=watcher.episodes_from_yesterday(),
        last_week=watcher.episodes_from_last_week(),
        coming_soon=watcher.episodes_for_next_week(),
    )
    if context['coming_soon'].count() < 5:
        context['coming_soon'] = watcher.episodes_coming_soon()[:7]
    return TemplateResponse(request, 'qsaui/home.html', context)


@require_GET
@login_required
def watchlist(request):
    context = dict(
        watchlist=request.user.watcher.series.all().order_by('name'),
    )
    return TemplateResponse(request, 'qsaui/watchlist.html', context)


@require_GET
@login_required
def search(request):
    q = request.GET.get('q')
    result = []
    if q:
        result = [
            (series,
             request.user.watcher.series.filter(tvdb_id=series.id).exists())
            for series in TvDB().search(q)]

    context = dict(result=result, q=q)
    return TemplateResponse(request, 'qsaui/results.html', context)


@require_http_methods(['GET', 'POST'])
@staff_member_required
def update_catalogue(request):
    if request.method == 'POST':
        form = UpdateCatalogueForm(request.POST)
        if form.is_valid():
            period = form.cleaned_data['period']

            output = StringIO()
            updated, unknown = CatalogueUpdater(stdout=output).update(
                period=period)

            period = 'last %s' % period if period != 'all' else 'everything'
            if updated:
                msg = 'Successfully updated %s (checked %s).' % (
                    ' and '.join(
                        '%s %s' % (len(v), k) for k, v in updated.iteritems()),
                    period)
                messages.success(request, msg)

                detail = 'Updated items:\n' + output.getvalue()
                messages.info(request, linebreaksbr(detail))
            else:
                msg = 'Nothing to update (checked %s).' % period
                messages.success(request, msg)

            return HttpResponseRedirect(reverse('home'))
    else:
        form = UpdateCatalogueForm()

    return TemplateResponse(request, 'qsaui/update.html', dict(form=form))


@require_http_methods(['GET', 'POST'])
@login_required
def series_detail(request, tvdb_id):
    series, _ = Series.objects.get_or_create(tvdb_id=tvdb_id, extended=True)
    if request.method == 'POST':
        if 'add-to-watchlist' in request.POST:
            return add_to_watchlist(request, series)
        elif 'remove-from-watchlist' in request.POST:
            return remove_from_watchlist(request, series)
        elif 'update' in request.POST:
            return update(request, series)
        else:
            messages.warning(request, 'Invalid operation')
            return HttpResponseRedirect('.')

    on_watchlist = request.user.watcher.series.filter(id=series.id).exists()
    context = dict(
        series=series, on_watchlist=on_watchlist,
        seasons=series.seasons())
    return TemplateResponse(request, 'qsaui/details.html', context)


def update(request, series):
    series.update_from_tvdb(extended=True)
    messages.success(
        request, '%s successfully updated' % series.name)
    return HttpResponseRedirect(
        reverse(series_detail, kwargs=dict(tvdb_id=series.tvdb_id)))


def add_to_watchlist(request, series):
    request.user.watcher.series.add(series)
    messages.success(
        request, '%s successfully added to your watchlist' % series.name)
    return HttpResponseRedirect(
        request.POST.get('next', reverse('your-watchlist')))


def remove_from_watchlist(request, series):
    request.user.watcher.series.remove(series)
    messages.success(
        request, '%s successfully removed from your watchlist' % series.name)
    return HttpResponseRedirect(
        request.POST.get('next', reverse('your-watchlist')))


@require_GET
@login_required
def series_episodes(request, tvdb_id, season):
    season = int(season)
    series = get_object_or_404(Series, tvdb_id=tvdb_id)
    seasons = list(series.seasons())
    episodes = Episode.objects.filter(season=season, series=series)
    context = dict(
        episodes=episodes.order_by('number'), series=series, season=season,
        seasons=seasons,
        prev_season=None if season == 1 else season - 1,
        next_season=None if season == seasons[-1] else season + 1)
    return TemplateResponse(request, 'qsaui/episodes.html', context)
