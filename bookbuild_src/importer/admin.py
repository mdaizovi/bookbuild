from django.contrib import admin
from import_export import resources
from import_export.admin import ExportMixin
from .models import Section, Neighborhood, Category, Blob

from django_admin_listfilter_dropdown.filters import (
    RelatedDropdownFilter,
    ChoiceDropdownFilter,
    DropdownFilter
)

simple_admins = [
    "Section", "Neighborhood", "Category",

]
for s in simple_admins:
    exec(
        "@admin.register({})\nclass {}Admin(admin.ModelAdmin):\n\tpass".format(
            s, s
        )
    )

class BlobResource(resources.ModelResource):

    class Meta:
        model = Blob
        #fields = [f.name for f in Blob._meta.fields]
        fields = ["title", "neighborhood__title", "section__title", "category__title", "priority"]
        export_order = fields
        skip_unchanged = True
        report_skipped = True

@admin.register(Blob)
class BlobAdmin(ExportMixin,admin.ModelAdmin):
    # Note: ExportMixin must be declared first.
    resource_class = BlobResource

    search_fields = ["title", "main_text"]

    list_display = [
        "title","neighborhood", "section","category","priority",
    ]

    list_filter = (
        ("neighborhood", RelatedDropdownFilter),
        ("section", RelatedDropdownFilter),
        ("category", RelatedDropdownFilter),
    )
