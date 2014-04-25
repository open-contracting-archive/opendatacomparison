from django.contrib import admin
from .models import (
    Field,
    TranslatedField,
    Concept,
    Datamap,
)


admin.site.register(Concept)
admin.site.register(Datamap)
admin.site.register(Field)
admin.site.register(TranslatedField)
