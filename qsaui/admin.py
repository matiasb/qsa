from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from qsaui.models import Episode, Series, Watcher


class WatcherInline(admin.StackedInline):
    model = Watcher
    can_delete = False


class UserAdmin(UserAdmin):
    inlines = (WatcherInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class SeriesAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'runtime', 'network', 'tvdb_id', 'imdb_id', 'completed')
    list_filter = ('runtime', 'network', 'completed')
    search_fields = ('name',)


class EpisodeAdmin(admin.ModelAdmin):
    date_hierarchy = 'first_aired'
    list_display = ('series', 'season', 'number', 'tvdb_id', 'imdb_id')
    list_filter = ('series', 'season')
    search_fields = ('series__name', 'season')


admin.site.register(Episode, EpisodeAdmin)
admin.site.register(Series, SeriesAdmin)
