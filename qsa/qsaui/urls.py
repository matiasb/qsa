from django.conf.urls import patterns, url


urlpatterns = patterns(
    'qsaui.views',
    url(r'^$', 'home', name='home'),
    url(r'^search/$', 'search', name='search'),
    url(r'^(?P<tvdb_id>\d+)/$', 'series_detail', name='series-detail'),
    url(r'^add/$', 'add_to_watchlist', name='add-to-watchlist'),
)
