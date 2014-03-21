from django.contrib import admin
from .models import Field, TranslatedField


class TranslatedFieldInline(admin.StackedInline):
    model = TranslatedField


class FieldAdmin(admin.ModelAdmin):
    inlines = [
        TranslatedFieldInline,
    ]

admin.site.register(Field, FieldAdmin)
