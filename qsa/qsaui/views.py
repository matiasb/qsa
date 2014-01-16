from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_GET, require_POST
from tvdbpy import TvDB

from qsaui.models import Series


@login_required
def home(request):
    context = dict(
        watchlist=request.user.watcher.series.all(),
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


@require_GET
@login_required
def series_detail(request, tvdb_id):
    series, _ = Series.objects.get_or_create(tvdb_id=tvdb_id, extended=False)
    context = dict(series=series)
    return TemplateResponse(request, 'qsaui/details.html', context)


@require_POST
@login_required
def add_to_watchlist(request):
    tvdb_id = request.POST.get('tvdb_id')
    series, _ = Series.objects.get_or_create(tvdb_id=tvdb_id, extended=True)
    request.user.watcher.series.add(series)

    messages.success(
        request, '%s successfully added to your watchlist' % series.name)
    return HttpResponseRedirect(reverse(home))
