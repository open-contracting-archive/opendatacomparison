from django.contrib import admin
from reversion.admin import VersionAdmin
from .models import (
    Field,
    TranslatedField,
    Concept,
    Datamap,
)


class DatamapAdmin(VersionAdmin):
    search_fields = ('dataset__title', 'format__title')


class FieldAdmin(VersionAdmin):
    search_fields = ('fieldname',)


class TranslatedFieldAdmin(VersionAdmin):
    search_fields = ('language', 'field__fieldname')


admin.site.register(Concept)
admin.site.register(Datamap, DatamapAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(TranslatedField, TranslatedFieldAdmin)
