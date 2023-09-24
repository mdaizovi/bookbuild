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

from .models import Author, Contributor, Book, Chapter, Image, StaticFile

# ===============================================================================
class ImageAdmin(admin.ModelAdmin):

    list_display = ("credit", "image_tag")
    search_fields = ("caption", "credit__lname", "credit__fname")
    list_filter = ("credit", "needsCitation")
    fields = (("caption"), "credit", "img", "image_tag")
    readonly_fields = ["image_tag"]


# ===============================================================================
class ChapterAdmin(admin.ModelAdmin):
    readonly_fields = ["chapter_url"]
    list_display = ("book", "title", "playOrder", "publish")
    list_filter = (("book", RelatedDropdownFilter),)

    actions = ["toggle_published"]

    def toggle_published(self, request, queryset):
        if request.POST.get("action") == "toggle_published":
            for obj in queryset:
                obj.publish = not obj.publish
                obj.save()
            self.message_user(
                request, "%s chapters successfully changed." % queryset.count()
            )
            return


# ===============================================================================

admin.site.register(Author)
admin.site.register(Contributor)
admin.site.register(Book)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(StaticFile)
admin.site.register(Image, ImageAdmin)
# admin.site.register(Section)
# admin.site.register(Subsection, SubsectionAdmin)
