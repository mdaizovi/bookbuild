import os
from collections import OrderedDict
from docx2python import docx2python
from io import StringIO
from docx import Document
from docx.shared import Inches

from django.conf import settings
from django.db.models import Count
from django.core.management.base import BaseCommand

from ...models import Section, Neighborhood, Category, Blob

# python manage.py export_text


class Command(BaseCommand):
    def handle(self, *args, **options):
        kwargs = {}

        filename = "export.docx"
        filepath = os.path.join(settings.BASE_DIR, "importer", "export", filename)

        document = Document()
        for n in (
            Neighborhood.objects.annotate(blob_count=Count("blob"))
            .filter(blob_count__gte=1)
            .order_by("-blob_count")
        ):

            document.add_heading(n.title, 0)
            cat = OrderedDict({"None": []})
            for b in Blob.objects.filter(
                neighborhood=n, priority__isnull=False
            ).order_by("category__title"):
                if not b.category:
                    cat["None"] = [b]
                elif b.category.title not in cat:
                    cat[b.category.title] = [b]
                else:
                    cat[b.category.title].append(b)

            category_accumulated_priority = {}
            for c, b_list in cat.items():
                accumulated_priority = sum(
                    [x.priority for x in b_list if x.priority is not None]
                )
                if accumulated_priority in category_accumulated_priority:
                    category_accumulated_priority[accumulated_priority].append(c)
                else:
                    category_accumulated_priority[accumulated_priority] = [c]
            sorted_priorities = list(category_accumulated_priority.keys())
            sorted_priorities.sort(reverse=True)

            for p in sorted_priorities:
                categories = category_accumulated_priority.get(p)
                for c in categories:
                    b_list = cat.get(c)

                    if len(b_list) > 0:
                        document.add_heading(c, level=3)
                        # sort blobs by priority
                        b_list.sort(key=lambda x: x.priority, reverse=True)
                        for b in b_list:
                            document.add_heading(b.title, level=4)
                            # title.add_run('bold').bold = True
                            document.add_paragraph(f"Priority: {str(b.priority)}")
                            document.add_paragraph(b.main_text)
                            # document.add_paragraph(b.footer_text)
                        document.add_paragraph("----")

            document.add_page_break()

        document.save(filepath)
