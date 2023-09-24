import boto3
import codecs
import errno
import os
import time
from shutil import copy, copytree, ignore_patterns
from collections import OrderedDict

from django.conf import settings
from django.template import Context, Template

from .models import Book, Chapter, Image

"""The code that actually builds the book.
"""

# -------------------------------------------------------------------------------
def copyanything(src, dst):
    try:
        copytree(src, dst, ignore=ignore_patterns('*.DS_Store'))
    except OSError as exc:  # python >2.5
        if exc.errno == errno.ENOTDIR:
            copy(src, dst)
        else:
            raise


# ===============================================================================
class EbookWriter:
    def __init__(self, book=None, get_assets=False):
        if not book:
            book = Book.objects.get(pk=1)
        self.book = book

        self.CSS_SNIPPET = ""
        for f in self.book.files.all():
            self.CSS_SNIPPET += (
                '<link href="%s" rel="stylesheet" type="text/css"/>' % f.relative_url
            )
        # self.CSS_SNIPPET = '<link href="css/stylesheet.css" rel="stylesheet" type="text/css"/>'

        self.get_assets = (
            get_assets  # whether or not to download images, css, etc from aws
        )

        self.BOOK_BASE_DIR = os.path.join(settings.BASE_DIR, "ebook_exporter")
        self.DESTINATION_MEDIA_PATH = os.path.join(
            self.BOOK_BASE_DIR, "Add2Epub", "OEBPS", "media"
        )
        self.TOC_FILE = os.path.join(self.BOOK_BASE_DIR, "Add2Epub", "toc.ncx")
        self.OPF_FILE = os.path.join(self.BOOK_BASE_DIR, "Add2Epub", "content.opf")
        # files and folders I made dynamically.
        self.FILES_TO_DELETE = [self.TOC_FILE, self.OPF_FILE]
        self.FOLDERS_TO_DELETE = [self.DESTINATION_MEDIA_PATH]

        self.metaDataDict = {
            # This data is used to create both toc.ncx and content.opf
            "title": self.book.title,
            "identifier": self.book.title or "isbn-000-0-000-00000-0",
            "creator": self.book.author_string,
            "publisher": "Team Kaffeeklatsch",
            "date": time.strftime("%Y-%m-%d"),
            "language": self.book.language or "en",
            "subject": self.book.subject or "",
            "description": "",
            "format": "0 pages",
            "type": "Text",
            "rights": "All rights reserved",
        }

    # -------------------------------------------------------------------------------
    def download_images_from_aws(self):
        # connect to the bucket
        s3_resource = boto3.resource("s3", region_name="us-east-1")
        my_bucket = s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
        s3_root_folder_prefix = "media"  # bucket inside root folder
        s3_folder_list = ["img"]  # root folder inside sub folders list

        print("About to start downloading images")
        for file in my_bucket.objects.filter(Prefix=s3_root_folder_prefix):
            if any(s in file.key for s in s3_folder_list):
                try:
                    path, filename = os.path.split(file.key)
                    new_home = os.path.join(settings.BASE_DIR, path)
                    if not os.path.exists(new_home):
                        try:
                            os.makedirs(new_home)  # Creates dirs recurcivly
                        except Exception as err:
                            print("exception making directory: ", err)
                    full_img_path = os.path.join(new_home, filename)
                    s3_resource.meta.client.download_file(
                        settings.AWS_STORAGE_BUCKET_NAME, file.key, full_img_path
                    )
                    print(file.key, " downloaded ")
                except Exception as err:
                    print("exception downloading file: ", err)
        print("Done downloading images")

    # -------------------------------------------------------------------------------
    def download_static_from_aws(self):

        # TODO i have no idea if this works.

        # connect to the bucket
        s3_resource = boto3.resource("s3", region_name="us-east-1")
        my_bucket = s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
        s3_root_folder_prefix = "media/bookbuild"  # bucket inside root folder
        s3_folder_list = ["static"]  # root folder inside sub folders list

        print("About to start downloading static")
        for file in my_bucket.objects.filter(Prefix=s3_root_folder_prefix):
            if any(s in file.key for s in s3_folder_list):
                try:
                    path, filename = os.path.split(file.key)
                    new_home = os.path.join(settings.BASE_DIR, path)
                    if not os.path.exists(new_home):
                        try:
                            os.makedirs(new_home)  # Creates dirs recurcivly
                        except Exception as err:
                            print("exception making directory: ", err)
                    full_img_path = os.path.join(new_home, filename)
                    s3_resource.meta.client.download_file(
                        settings.AWS_STORAGE_BUCKET_NAME, file.key, full_img_path
                    )
                    print(file.key, " downloaded ")
                except Exception as err:
                    print("exception downloading file: ", err)
        print("Done downloading static")

    # -------------------------------------------------------------------------------
    def writeComponent(self, component_type, chapter=None):
        # component_type may be cover, section, chapter, contents, contribute
        ctx = Context({"book": self.book, "CSS_SNIPPET": self.CSS_SNIPPET})

        html_path_list = [
            settings.BASE_DIR,
            "templates",
            "ebook_exporter",
            self.book.book_type,
            component_type + "Base.html",
        ]

        if component_type == "cover":
            html_destination = os.path.join(
                self.BOOK_BASE_DIR, "Add2Epub", "OEBPS/001_cover.html"
            )
        elif component_type == "chapter" and chapter:
            if hasattr(chapter, "section"):
                html_path_list = [
                    settings.BASE_DIR,
                    "templates",
                    "ebook_exporter",
                    self.book.book_type,
                    "sectionBase.html",
                ]
                ctx.update(
                    {
                        "section": chapter.section,
                        "subsections": chapter.section.subsection_set.filter(
                            publish=True
                        ).order_by("order"),
                    }
                )
            else:
                ctx.update({"chapter": chapter})
            html_destination = os.path.join(self.BOOK_BASE_DIR, "Add2Epub", chapter.src)
        elif component_type == "contents":
            exclude = ["Title Page", "Copyright", "Contents"]
            chapters_all = (
                self.book.chapter_set.filter(publish=True)
                .order_by("playOrder")
                .exclude(title__in=exclude)
            )
            chapters = OrderedDict()
            for c in chapters_all:
                if hasattr(c, "section"):
                    chapters.update(
                        {
                            c: list(
                                c.section.subsection_set.filter(publish=True).order_by(
                                    "order"
                                )
                            )
                        }
                    )
                else:
                    chapters.update({c: []})
            ctx.update({"chapters": chapters})
            chapter = Chapter.objects.get(book=self.book, title="Contents")
            html_destination = os.path.join(self.BOOK_BASE_DIR, "Add2Epub", chapter.src)

        html_file = os.path.join(*html_path_list)
        if not os.path.exists(html_file):
            # Remove book type if is generic template that exists in all book types.
            html_path_list.pop(-2)
            html_file = os.path.join(*html_path_list)

        f = codecs.open(html_file, "r")
        template_html = f.read()
        template = Template(template_html)
        f = open(html_destination, "w")
        f.write(template.render(ctx))
        # Add html filename to list of files to clean up.
        self.FILES_TO_DELETE.append(html_destination)

        return template.render(ctx)

    # -------------------------------------------------------------------------------
    def writeOPF(self):
        """Writes content.opf based on Chapter data from db
        """
        spinelist = ["cover"]

        opf_str = """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\
                <package xmlns="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/" unique-identifier="bookid" version="2.0">"""

        opf_str += "<metadata>"
        for attr in [
            "title",
            "identifier",
            "creator",
            "publisher",
            "date",
            "language",
            "subject",
            "description",
            "format",
            "type",
            "rights",
        ]:
            opf_str += (
                "<dc:"
                + attr
                + ">"
                + str(self.metaDataDict.get(attr))
                + "</dc:"
                + attr
                + ">"
            )
        opf_str += "<meta content='cover-image' name='cover'/></metadata>"

        opf_str += "<manifest><item href='toc.ncx' id='ncx' media-type='application/x-dtbncx+xml'/>"

        # TODO: # do I even need to list images in img directory? media ones show up just fine, but i never list them.
        for dirname, media_type in {
            "css": "text/css",
            "fonts": "application/vnd.ms-opentype",
            "images": "image/jpeg",
        }.items():
            this_index = 0
            this_dir = os.path.join(self.BOOK_BASE_DIR, "Add2Epub", "OEBPS", dirname)
            for f in os.listdir(this_dir):
                this_index += 1
                opf_str += (
                    "<item href='OEBPS/"
                    + dirname
                    + "/"
                    + f
                    + "' id = '"
                    + dirname[0]
                    + str(this_index)
                    + "' media-type='"
                    + media_type
                    + "'/>"
                )

        if self.book.cover:
            cover_filename = "media/" + self.book.cover.get_file_name()
        else:
            cover_filename = "images/cover.jpg"
        opf_str += (
            "<item href='OEBPS/"
            + cover_filename
            + "' id = 'cover-image' media-type='image/jpeg'/>"
        )

        # incude cover html
        opf_str += "<item href='OEBPS/001_cover.html' id='HTML1' media-type='application/xhtml+xml'/>"
        spinelist.append("HTML1")

        for c in Chapter.objects.filter(book=self.book, publish=True):
            html_id = "HTML" + str(c.pk)
            spinelist.append(html_id)
            opf_str += (
                "<item href='"
                + str(c.src)
                + "' id='"
                + html_id
                + "' media-type='application/xhtml+xml'/>"
            )
        opf_str += "</manifest><spine toc='ncx'>"

        for s in spinelist:
            opf_str += "<itemref idref='" + s + "'/>"
        opf_str += "</spine>"

        opf_str += "<guide><reference href='OEBPS/001_cover.html' title='cover' type='cover'/></guide></package>"

        print("done writing everyhting?")

        with open(self.OPF_FILE, "w") as opf:
            opf.write(opf_str)

    # -------------------------------------------------------------------------------
    def writeTOC(self):
        """Writes toc.ncx based on Chapter data from db
        """

        toc_str = """<?xml version="1.0" encoding="UTF-8"?>\
        <!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"\
        "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">\
        <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\
        <head>\
        <meta name="dtb:uid" content="ISBN:"/>\
        <meta name="dtb:depth" content="1"/>\
        <!-- <meta name="dtb:totalPageCount" content=""/>\
        <meta name="dtb:maxPageNumber" content=""/> -->\
        </head>"""

        toc_str += "<docTitle><text>" + self.book.title + "</text></docTitle>"
        toc_str += "<navMap>"

        toc_str += "<navPoint id='navPoint-1' playOrder='1'>"
        toc_str += "<navLabel><text>Cover</text></navLabel><content src='OEBPS/001_cover.html'/></navPoint>"
        self.book.sequentialize()
        for c in list(self.book.chapter_set.filter(publish=True).order_by("playOrder")):
            toc_str += (
                "<navPoint id='navPoint-"
                + str(c.playOrder)
                + "' playOrder='"
                + str(c.playOrder)
                + "'>"
            )
            toc_str += "<navLabel><text>" + str(c.title) + "</text></navLabel>"
            toc_str += "<content src='" + str(c.src) + "'/></navPoint>"

        toc_str += "</navMap></ncx>"
        toc = open(self.TOC_FILE, "w")
        toc.write(toc_str)
        toc.close()

    # -------------------------------------------------------------------------------
    def buildNewEpub(self, thisTitle="newbook"):
        """Builds new epub
        """

        # 1. Make new dir for new epub.
        book_dir = os.path.join(self.BOOK_BASE_DIR, "epub_build")
        if os.path.exists(book_dir):
            print("build already exists. Please remove or delete old build.")
        else:
            # 2. Copy and move the standard dirs!
            copyanything(os.path.join(self.BOOK_BASE_DIR, "Add2Epub"), book_dir)

            # 3. Make new files! First toc.ncx and content.opf, then recipe content, then indices?
            newBookDir = os.path.join(self.BOOK_BASE_DIR, thisTitle)

            # 4. compress
            shutil.make_archive(newBookDir, "zip", book_dir)

            # 5. then change from zip to epub
            os.rename(
                os.path.join(self.BOOK_BASE_DIR, (thisTitle + ".zip")),
                os.path.join(self.BOOK_BASE_DIR, (thisTitle + ".epub")),
            )

            # 6. remove old folder
            shutil.rmtree(book_dir)

    # -------------------------------------------------------------------------------
    def cleanUp(self):
        """
        After epub is written,
        delete files and folders I wrote dynamically to Add2Epub, so won't confuse and conflict.
        NOTES:
                os.remove() will remove a file.
                os.rmdir() will remove an empty directory.
                shutil.rmtree() will delete a directory and all its contents.
        """

        for f in self.FILES_TO_DELETE:
            os.remove(f)
        for f in self.FOLDERS_TO_DELETE:
            shutil.rmtree(f)
        print("All cleaned up!")

    # -------------------------------------------------------------------------------
    def writeBook(self):
        """For some reason calling writeTOC() inside of buildNewEpub() makes the toc not work,
        but this is fine.
        If contributor list given, will only do those contributor's sections.
        """

        # NOTE: I build book form whatever images and html i can find in OEBPS

        # by the time i get here, html and images should be ready.

        # Copy uploaded images from media root to
        # copyanything(MEDIA_ROOT, self.DESTINATION_MEDIA_PATH)
        # so url will be same.

        if self.get_assets:
            self.download_images_from_aws()
            self.download_static_from_aws()

        imageList = Book.objects.get_images(self.book)
        # make folder media
        if not os.path.exists(self.DESTINATION_MEDIA_PATH):
            os.makedirs(self.DESTINATION_MEDIA_PATH)
        # TODO: write this better later. for now I'm just including all images in Flo's book.
        # if len(imageList) > 0:
        if len(imageList) > 1:
            for i in imageList:
                # NOTE using i.img.file always called online location and didn't work offline.
                local_location = os.path.join(settings.MEDIA_ROOT, str(i.img.name))
                copyanything(local_location, self.DESTINATION_MEDIA_PATH)
        else:
            for i in os.listdir(settings.MEDIA_ROOT + "/img/"):
                copyanything(
                    settings.MEDIA_ROOT + "/img/" + i, self.DESTINATION_MEDIA_PATH
                )

        filelist = self.book.files.all()
        for f in filelist:
            DESTINATION_FILE_PATH = os.path.join(
                self.BOOK_BASE_DIR, "Add2Epub", "OEBPS", f.file_type
            )
            if not os.path.exists(DESTINATION_FILE_PATH):
                os.makedirs(DESTINATION_FILE_PATH)
            local_location = os.path.join(
                settings.MEDIA_ROOT, "ebook_exporter", "static", f.filename
            )
            copyanything(local_location, DESTINATION_FILE_PATH)

        self.writeComponent("cover")
        for c in (
            self.book.chapter_set.filter(publish=True)
            .order_by("playOrder")
            .exclude(title__in=["Contents", "Contributors"])
        ):
            self.writeComponent(component_type="chapter", chapter=c)
        if self.book.book_type == "CK":
            if Chapter.objects.filter(title="Contents", book=self.book).exists():
                self.writeComponent("contents")
            if Chapter.objects.filter(title="Contributors", book=self.book).exists():
                self.writeComponent("contribute")

        self.writeOPF()
        self.writeTOC()
        self.buildNewEpub(self.book.slugify_title())

        self.cleanUp()


# python manage.py export_ebook --book 1  --get_assets
