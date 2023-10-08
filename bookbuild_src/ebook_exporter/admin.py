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

from .models import Author, Book, Chapter, Image, StaticFile, Section, Subsection

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
    list_display = ("book", "title", "playOrder")
    list_filter = (("book", RelatedDropdownFilter),)

# ===============================================================================

# These admins should be put back someday
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Section)
admin.site.register(Subsection)
admin.site.register(StaticFile)
admin.site.register(Image, ImageAdmin)

# These models don't exist right not
# admin.site.register(Contributor)
