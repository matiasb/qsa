from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from qsaui.models import Watcher


class WatcherInline(admin.StackedInline):
    model = Watcher
    can_delete = False


class UserAdmin(UserAdmin):
    inlines = (WatcherInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
