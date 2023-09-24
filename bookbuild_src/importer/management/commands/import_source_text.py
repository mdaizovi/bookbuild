import os
from collections import OrderedDict
from docx2python import docx2python
from io import StringIO

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import Section, Neighborhood, Category, Blob

# python manage.py import_source_text --filename 03-ausflug.docx --dryrun


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--filename", type=str, help="file name relative to BASE_DIR"
        )

        parser.add_argument(
            "--verbose", action="store_true", help="True if you want lots of output"
        )

        parser.add_argument(
            "--dryrun",
            action="store_true",
            help="True if you don't want to save anything",
        )

    def handle(self, *args, **options):
        kwargs = {}
        filename = options["filename"]
        verbose = options["verbose"]
        dryrun = options["dryrun"]

        if verbose:
            print(f"--Starting to import {filename}")

        filepath = os.path.join(settings.BASE_DIR, "importer", "source", filename)
        # print(f"filepath: {filepath}")

        doc_result = docx2python(f"{filepath}")
        body = [x.strip() for x in doc_result.body[0][0][0] if len(x) > 1]
        # print(body)
        section_title = body[0]
        section, _ = Section.objects.get_or_create(title=section_title)
        # print(f"{section}")
        if not dryrun:
            section.save()

        titles = {body.index(x): x for x in body if "[" in x and "]" in x}
        sorted = list(titles.keys())
        sorted.sort()
        sorted_titles = OrderedDict()
        for t in sorted:
            sorted_titles[t] = titles.get(t)

        i = 0
        # for element in body[1:20]:
        for element in body[1:]:
            i += 1
            if i in sorted:
                # print(f"i: {i}")
                if i == sorted[-1]:
                    next_index = None
                else:
                    this_sorted_index = sorted.index(i)
                    next_index = sorted[this_sorted_index + 1]
                if i == sorted[0]:
                    previous_index = None
                else:
                    previous_index = sorted[this_sorted_index - 1]
                # print(f"next: {next_index}")
                # print(f"previous: {previous_index}")
                if next_index:
                    this_section = body[i:next_index]
                else:
                    this_section = body[i:]

                category_title = None
                category_body = None
                if previous_index:
                    previous_section = body[previous_index:i]
                    # print("previous_section")
                    # print(previous_section)
                    if section_title in previous_section:
                        title_position = previous_section.index(section_title)
                        category_title = previous_section[title_position + 1]
                        category_body = previous_section[title_position + 2 :]
                else:
                    category_title = body[1]
                    category_body = body[2:i]
                if category_title and category_body:
                    category, _ = Category.objects.get_or_create(
                        title=category_title, main_text=category_body
                    )
                    if not dryrun:
                        category.save()
                    # print(f"\n---------\n{category}\n---------")
                    # print(f"{category.main_text}")

                title_list = sorted_titles.get(i).split("[")
                blob_title = title_list[0]
                neighborhood_title = title_list[1][:-1]

                neighborhood, _ = Neighborhood.objects.get_or_create(
                    title=neighborhood_title
                )
                if not dryrun:
                    neighborhood.save()
                # print(f"\n{neighborhood}\n")

                # footer is the first part of this_section thst contains href, until end.
                hi = -1
                for e in this_section:
                    hi += 1
                    if "href" in e:
                        break
                main_text_list = this_section[1:hi]
                footer_text_list = this_section[hi:]

                main_text = "\n".join(main_text_list)
                footer_text = "\n".join(footer_text_list)

                blob, created = Blob.objects.get_or_create(title=blob_title)
                if created:
                    blob_dict = {
                        "category": category,
                        "neighborhood": neighborhood,
                        "section": section,
                        "main_text": main_text,
                        "footer_text": footer_text,
                    }
                    for k, v in blob_dict.items():
                        setattr(blob, k, v)
                        blob.save()

                if not dryrun:
                    blob.save()

                # print(f"\n{blob}\n")
                for v in [
                    "category",
                    "neighborhood",
                    "section",
                    "title",
                    "main_text",
                    "footer_text",
                ]:
                    attr = getattr(blob, v)
                    # print(f"{v}: {attr}")
                # print("\n\n")

        if verbose:
            print(f"--finished importing {filename}")
