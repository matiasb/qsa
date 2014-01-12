from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    'qsaui.views',
    url(r'^$', 'home', name='home'),
    url(r'^search/$', 'search', name='search'),
)
