import os
from collections import OrderedDict
from docx2python import docx2python
from io import StringIO
from docx import Document
from docx.shared import Inches

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import Section, Neighborhood, Category, Blob

#python manage.py export_text 

class Command(BaseCommand):

    def handle(self, *args, **options):
        kwargs = {}

        filename = "export.docx"
        filepath = os.path.join(settings.BASE_DIR, "importer", "export", filename)

        document = Document()
        for n in Neighborhood.objects.all():
            document.add_heading(n.title, 0)
            cat = OrderedDict({"None":[]})
            for b in Blob.objects.filter(neighborhood = n).order_by('category__title'):
                if not b.category:
                    cat["None"] = [b]
                elif b.category.title not in cat:
                    cat[b.category.title] = [b]
                else:
                    cat[b.category.title].append(b)

            for c, b_list in cat.items():
                if len(b_list) > 0:
                    document.add_heading(c, level=3)
                    for b in b_list:
                        document.add_heading(b.title, level=4)
                        #title.add_run('bold').bold = True
                        document.add_paragraph(f"Priority: {str(b.priority)}")
                        document.add_paragraph(b.main_text)
                        #document.add_paragraph(b.footer_text)
                    document.add_paragraph("----")

            document.add_page_break()

        document.save(filepath)

