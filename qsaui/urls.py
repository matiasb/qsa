from django.urls import path

import qsaui.views


urlpatterns = [
    path('', qsaui.views.home, name='home'),
    path('watchlist/', qsaui.views.watchlist, name='your-watchlist'),
    path('search/', qsaui.views.search, name='search'),
    path('update/', qsaui.views.update_catalogue, name='update-catalogue'),
    path('<int:tvdb_id>/', qsaui.views.series_detail, name='series-detail'),
    path('<int:tvdb_id>/<int:season>/', qsaui.views.series_episodes,
         name='series-episodes'),
]
