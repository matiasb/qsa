from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.http import require_GET, require_http_methods
from tvdbpy import TvDB

from qsaui.models import Series, Episode


@require_GET
@login_required
def home(request):
    watcher = request.user.watcher
    context = dict(
        yesterday=watcher.episodes_from_yesterday().order_by('name'),
        last_week=watcher.episodes_from_last_week().order_by(
            '-first_aired', 'name'),
        next_week=watcher.episodes_for_next_week().order_by(
            'first_aired', 'name'),
    )
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
@login_required
def series_detail(request, tvdb_id):
    series, _ = Series.objects.get_or_create(tvdb_id=tvdb_id, extended=True)
    if request.method == 'POST':
        if 'add-to-watchlist' in request.POST:
            return add_to_watchlist(request, series)
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
    return HttpResponseRedirect(reverse(home))


@require_GET
@login_required
def series_episodes(request, tvdb_id, season):
    series = get_object_or_404(Series, tvdb_id=tvdb_id)
    episodes = Episode.objects.filter(season=season, series=series)
    context = dict(episodes=episodes, series=series, season=season)
    return TemplateResponse(request, 'qsaui/episodes.html', context)
