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
    "Section",

]
for s in simple_admins:
    exec(
        "@admin.register({})\nclass {}Admin(admin.ModelAdmin):\n\tsearch_fields = ['title']".format(
            s, s
        )
    )


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ("title",)
        export_order = fields
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ("title",)

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource

class NeighborhoodResource(resources.ModelResource):
    class Meta:
        model = Neighborhood
        fields = ("title",)
        export_order = fields
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ("title",)

@admin.register(Neighborhood)
class NeighborhoodAdmin(ImportExportModelAdmin):
# class BlobAdmin(ExportMixin,admin.ModelAdmin):
    # Note: ExportMixin must be declared first.
    resource_class = NeighborhoodResource
    list_display = [
        "title",
    ]

class BlobResource(resources.ModelResource):

    # categories = fields.Field(
    #     column_name = 'categories',
    #     attribute='categories',
    #     widget=ManyToManyWidget(Category, field='title', separator=';')
    # )
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, field='title'))    
    
    neighborhood = fields.Field(
        column_name='neighborhood',
        attribute='neighborhood',
        widget=ForeignKeyWidget(Neighborhood, field='title'))

    class Meta:
        model = Blob
        fields = ("title", "neighborhood", "category", "priority")
        export_order = fields
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ("title",)
        #use_natural_foreign_keys = True

@admin.register(Blob)
class BlobAdmin(ImportExportModelAdmin):
# class BlobAdmin(ExportMixin,admin.ModelAdmin):
    # Note: ExportMixin must be declared first.
    resource_class = BlobResource

    search_fields = ["title", "main_text"]

    list_display = [
        "title", "neighborhood","category", "priority","has_text","soft_delete"
    ]
    #filter_horizontal = ('categories',)
    list_filter = (
        ("neighborhood", RelatedDropdownFilter),
        ("section", RelatedDropdownFilter),
        ("soft_delete", DropdownFilter),
        ("category", RelatedDropdownFilter),
    )
