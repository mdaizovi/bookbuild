from django.contrib import admin
from .models import Section, Neighborhood, Category, Blob

# from django_admin_listfilter_dropdown.filters import (
#     RelatedDropdownFilter,
#     ChoiceDropdownFilter,
# )

simple_admins = [
    "Section", "Neighborhood", "Category",

]
for s in simple_admins:
    exec(
        "@admin.register({})\nclass {}Admin(admin.ModelAdmin):\n\tpass".format(
            s, s
        )
    )

@admin.register(Blob)
class BlobAdmin(admin.ModelAdmin):
    search_fields = ["title", "main_text"]
    # list_filter = (
    #     ("task_type", ChoiceDropdownFilter),
    #     ("exercise_type", ChoiceDropdownFilter),
    # )    