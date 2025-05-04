from django.core.management.base import BaseCommand

from ...models import Book
from ...writer.ebook_writer import EbookWriter
from django.conf import settings

# python manage.py export_ebook --book 1
# or BUT 555 tips does not have any aws buckets, get_assets does nothing
# python manage.py export_ebook --book 1 --get_assets
# or
# python manage.py export_ebook --book 1 --verbose


class Command(BaseCommand):
    help = "Writes book from database to ebook"

    def add_arguments(self, parser):
        parser.add_argument("--book", type=int, help="ID of which book to export")

        parser.add_argument(
            "--get_assets",
            action="store_true",
            help="Add if you need to download assets (images, css, etc) from AWS",
        )

        parser.add_argument(
            "--verbose", action="store_true", help="Add if you want output on console",
        )

        parser.add_argument(
            "--language", type=str, default=settings.LANGUAGE_CODE, help="Language to output the book in",
        )

    def handle(self, *args, **options):
        kwargs = {}

        if options["book"]:
            try:
                book = Book.objects.get(pk=options["book"])
            except:
                book = Book.objects.all().first()
        else:
            book = Book.objects.all().first()

        if options["get_assets"]:
            get_assets = options["get_assets"]
        else:
            get_assets = False

        if options["verbose"]:
            verbose = options["verbose"]
        else:
            verbose = False

        language = options["language"]

        print("--Starting to export %s in %s" % (book.title, language)) if verbose else None
        writer = EbookWriter(language=language, book=book, get_assets=get_assets, verbose=verbose)
        writer.writeBook()
        print("\n\n--Finished exporting %s" % (book.title)) if verbose else None
