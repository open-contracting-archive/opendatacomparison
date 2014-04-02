from django.contrib import admin
from nested_inlines.admin import (
    NestedModelAdmin,
    NestedStackedInline,
    NestedTabularInline,
)
from .models import (
    Field,
    TranslatedField,
    Concept,
    Datamap,
)


class TranslatedFieldInline(NestedTabularInline):
    model = TranslatedField
    extra = 1


class FieldAdmin(NestedStackedInline):
    model = Field
    inlines = [
        TranslatedFieldInline,
    ]


class DatamapAdmin(NestedModelAdmin):
    inlines = [FieldAdmin, ]


class FieldAdminStandalone(admin.ModelAdmin):
    inlines = [TranslatedFieldInline, ]


admin.site.register(Concept)
admin.site.register(Datamap, DatamapAdmin)
admin.site.register(Field, FieldAdminStandalone)
