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

from .models import Author, Contributor, Book, Chapter, Section, Image, StaticFile

# ===============================================================================
class RecipeAdmin(OrderedModelAdmin):
    def content_div(self, obj):
        return str(obj.get_content_div_from_source())

    def has_author_questions(self, instance):
        """Temporary field, to assist in keeping track of which recipes  have questions
        """
        if instance.author_questions:
            return True

    has_author_questions.boolean = True

    list_display = (
        "title",
        "permission",
        "joy_edited",
        "has_author_questions",
        "contributor",
        "publish",
        "move_up_down_links",
        "order",
        "halfpage",
    )
    search_fields = ("title", "contributor__lname")

    list_filter = (
        # for ordinary fields
        ("publish", DropdownFilter),
        ("permission", DropdownFilter),
        ("section", RelatedDropdownFilter),
        ("contributor", RelatedDropdownFilter),
        ("section", RelatedDropdownFilter),
        ("joy_edited", DropdownFilter),
    )
    list_display_links = list_display
    fields = (
        "title",
        "book",
        ("permission", "publish", "joy_edited"),
        ("contributor", "section"),
        ("halfpage"),
        ("img", "img_lower"),
        "ingredients_html",
        "ingredients_html2",
        "steps_html",
        "intro",
        "author_questions",
    )


# ===============================================================================
class ImageAdmin(admin.ModelAdmin):

    list_display = ("credit", "image_tag", "permission")
    search_fields = ("caption", "credit__lname", "credit__fname")
    list_filter = ("credit", "permission", "needsCitation")
    fields = (("caption"), ("permission", "credit"), "img", "image_tag")
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
admin.site.register(Section)
admin.site.register(StaticFile)
admin.site.register(Image, ImageAdmin)
admin.site.register(Recipe, RecipeAdmin)
