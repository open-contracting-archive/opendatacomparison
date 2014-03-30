from django.contrib import admin
from .models import (
    Field,
    TranslatedField,
    Concept,
    Datamap,
)


class TranslatedFieldInline(admin.StackedInline):
    model = TranslatedField
    extra = 1


class FieldAdmin(admin.ModelAdmin):
    inlines = [
        TranslatedFieldInline,
    ]

admin.site.register(Field, FieldAdmin)
admin.site.register(Concept)
admin.site.register(Datamap)
