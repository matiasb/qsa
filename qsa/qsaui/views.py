from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_GET

from tvdbpy import TvDB

@login_required
def home(request):
    context = dict(
        series=request.user.watcher.series.all(),
    )
    return TemplateResponse(request, 'qsaui/home.html', context)


@require_GET
def search(request):
    q = request.GET.get('q')
    result = []
    if q:
        result = TvDB().search(q)

    context = dict(result=result, q=q)
    return TemplateResponse(request, 'qsaui/results.html', context)
