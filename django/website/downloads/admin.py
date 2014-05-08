from django.contrib import admin
from reversion.admin import VersionAdmin
from .models import Link, Click


class ClickAdmin(admin.ModelAdmin):
    list_display = ('link', 'time', 'username')


class LinkAdmin(VersionAdmin):
    pass

admin.site.register(Link, LinkAdmin)
admin.site.register(Click, ClickAdmin)
