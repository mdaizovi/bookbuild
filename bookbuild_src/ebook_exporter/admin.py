from django.contrib import admin
from django_admin_listfilter_dropdown.filters import (
    DropdownFilter,
    RelatedDropdownFilter,
    ChoiceDropdownFilter,
)

# for image
# from django.contrib.admin.widgets import AdminFileWidget
# from django.utils.translation import ugettext as _
# from django.utils.safestring import mark_safe
from ordered_model.admin import OrderedModelAdmin

from .models import (
    Author,
    Book,
    Chapter,
    Image,
    StaticFile,
    Section,
    Subsection,
    FooterDetail,
)

# ===============================================================================
class ImageAdmin(admin.ModelAdmin):

    list_display = ("image_tag",)
    search_fields = ("caption",)
    list_filter = ("needsCitation",)
    fields = (("caption"), "img", "image_tag")
    readonly_fields = ["image_tag"]


# ===============================================================================
class ChapterAdmin(admin.ModelAdmin):
    readonly_fields = ["chapter_url"]
    list_display = ("book", "title", "playOrder", "chapter_type")
    list_filter = (("book", RelatedDropdownFilter),)


# ===============================================================================
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "chapter")
    list_filter = (("chapter", RelatedDropdownFilter),)


# ===============================================================================
class FooterDetailInline(admin.TabularInline):  # or admin.StackedInline
    model = FooterDetail
    extra = 1  # Number of empty forms to display


# ===============================================================================
class SubsectionAdmin(admin.ModelAdmin):
    search_fields = ("title", "priority")
    list_display = ("title", "section", "priority", "order")
    list_filter = (
        ("section", RelatedDropdownFilter),
        ("section__chapter", RelatedDropdownFilter),
    )
    inlines = [FooterDetailInline]  # Add the inline class here


# ===============================================================================

# These admins should be put back someday
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Subsection, SubsectionAdmin)
admin.site.register(StaticFile)
# admin.site.register(Image, ImageAdmin)

# These models don't exist right not
# admin.site.register(Contributor)
