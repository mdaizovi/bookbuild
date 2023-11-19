from django.core.management.base import BaseCommand

from ...models import Book
from ...writer.ebook_writer import EbookWriter

# python manage.py export_ebook --book 1
# or
# python manage.py export_ebook --book 1 --get_assets


class Command(BaseCommand):
    help = "Writes book from database to ebook"

    def add_arguments(self, parser):
        parser.add_argument("--book", type=int, help="ID of which book to export")

        parser.add_argument(
            "--get_assets",
            action="store_true",
            help="Add if you need to download assets (images, css, etc) from AWS",
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

        #print("--Starting to export %s" % (book.title))
        writer = EbookWriter(book=book, get_assets=get_assets)
        writer.writeBook()
        #print("\n\n--Finished exporting %s" % (book.title))
