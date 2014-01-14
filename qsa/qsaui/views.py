from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_GET, require_http_methods
from tvdbpy import TvDB

from qsaui.models import Series


@login_required
def home(request):
    context = dict(
        series=request.user.watcher.series.all(),
    )
    return TemplateResponse(request, 'qsaui/home.html', context)


@require_GET
@login_required
def search(request):
    q = request.GET.get('q')
    result = []
    if q:
        result = TvDB().search(q)

    context = dict(result=result, q=q)
    return TemplateResponse(request, 'qsaui/results.html', context)


@require_http_methods(['GET', 'POST'])
@login_required
def series_detail(request, tvdb_id):
    series, _ = Series.objects.get_or_create(tvdb_id=tvdb_id, extended=False)
    if request.method == 'POST':
        if 'add-to-watchlist' in request.POST:
            return add_to_watchlist(request, series)
        elif 'update' in request.POST:
            return update(request, series)
        else:
            messages.warning(request, 'Invalid operation')
            return HttpResponseRedirect('.')

    watched = request.user.watcher.series.filter(id=series.id).exists()
    context = dict(series=series, watched=watched)
    return TemplateResponse(request, 'qsaui/details.html', context)


def update(request, series):
    series.update_from_tvdb(extended=True)
    messages.success(
        request, '%s successfully updated' % series.name)
    return HttpResponseRedirect(
        reverse(series_detail, kwargs=dict(tvdb_id=series.tvdb_id)))


def add_to_watchlist(request, series):
    request.user.watcher.series.add(series)
    series.update_from_tvdb(extended=True)
    messages.success(
        request, '%s successfully added to your watchlist' % series.name)
    return HttpResponseRedirect(reverse(home))
