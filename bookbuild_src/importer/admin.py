from django.contrib import admin
from import_export.admin import ExportMixin, ImportExportModelAdmin
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

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
        "@admin.register({})\nclass {}Admin(admin.ModelAdmin):\n\tsearch_fields = ['title']".format(
            s, s
        )
    )

class BlobResource(resources.ModelResource):

    categories = fields.Field(
        column_name = 'categories',
        attribute='categories',
        widget=ManyToManyWidget(Category, field='title', separator=';')
    )
    # section = fields.Field(
    #     column_name='section',
    #     attribute='section',
    #     widget=ForeignKeyWidget(Section, field='title'))    
    
    neighborhood = fields.Field(
        column_name='neighborhood',
        attribute='neighborhood',
        widget=ForeignKeyWidget(Neighborhood, field='title'))

    class Meta:
        model = Blob
        fields = ("id","title", "neighborhood", "categories", "priority")
        export_order = fields
        skip_unchanged = True
        report_skipped = True

@admin.register(Blob)
class BlobAdmin(ImportExportModelAdmin):
# class BlobAdmin(ExportMixin,admin.ModelAdmin):
    # Note: ExportMixin must be declared first.
    resource_class = BlobResource

    search_fields = ["title", "main_text"]

    list_display = [
        "title", "section","neighborhood","priority","soft_delete"
    ]
    filter_horizontal = ('categories',)
    list_filter = (
        ("neighborhood", RelatedDropdownFilter),
        ("section", RelatedDropdownFilter),
        #("category", RelatedDropdownFilter),
        ("soft_delete", DropdownFilter)
    )
