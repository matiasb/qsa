from django.conf.urls import patterns, url


urlpatterns = patterns(
    'qsaui.views',
    url(r'^$', 'home', name='home'),
    url(r'^search/$', 'search', name='search'),
    url(r'^add/$', 'add_to_watchlist', name='add-to-watchlist'),
)
