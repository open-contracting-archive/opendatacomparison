from django.contrib import admin
from .models import Link, Click


class ClickAdmin(admin.ModelAdmin):
    list_display = ('link', 'time', 'username')


admin.site.register(Link)
admin.site.register(Click, ClickAdmin)
