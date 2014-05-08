from django.contrib import admin
from reversion.admin import VersionAdmin

from package.models import (
    Category,
    Package,
    TranslatedPackage,
    Version,
    Format,
)

class TranslatedPackageAdmin(VersionAdmin):
    list_display = ("package", "language", "title")
    search_fields = ("package__title", "language", "title")


class TranslatedPackageInline(admin.StackedInline):
    model = TranslatedPackage
    extra = 1


class PackageAdmin(VersionAdmin):

    save_on_top = True
    search_fields = ("title",)
    list_filter = ("category",)
    list_display = ("title", "created", )
    date_hierarchy = "created"

    inlines = [
        TranslatedPackageInline
    ]


class CommitAdmin(admin.ModelAdmin):
    list_filter = ("package",)


class VersionLocalAdmin(admin.ModelAdmin):
    search_fields = ("package__title",)


class PackageExampleAdmin(admin.ModelAdmin):

    list_display = ("title", )
    search_fields = ("title",)


admin.site.register(Category, VersionAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(TranslatedPackage, TranslatedPackageAdmin)
admin.site.register(Version, VersionLocalAdmin)
admin.site.register(Format)
