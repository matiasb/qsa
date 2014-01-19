from django.conf.urls import patterns, url


urlpatterns = patterns(
    'qsaui.views',
    url(r'^$', 'home', name='home'),
    url(r'^watchlist/$', 'watchlist', name='your-watchlist'),
    url(r'^search/$', 'search', name='search'),
    url(r'^(?P<tvdb_id>\d+)/$', 'series_detail', name='series-detail'),
)
