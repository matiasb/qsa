import allauth.urls
from django.contrib import admin
from django.urls import include, path

import qsaui.urls
import qsaui.views


urlpatterns = [
    path('', qsaui.views.home),
    path('qsa/', include(qsaui.urls)),
    path('accounts/', include(allauth.urls)),
    path('admin/', admin.site.urls),
]
