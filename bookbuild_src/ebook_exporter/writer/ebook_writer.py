# -*- coding: utf-8 -*-
import codecs
import os
import time

from django.conf import settings
from django.template import Context, Template
from .utils import (
    cleanUp,
    copyanything,
    compress,
    download_images_from_aws,
    download_static_from_aws,
)
from .queries import BookQueries

# INSTRUCTIONS FOR FLO

# virtualenv venvironment
# cd..
# pip install -r requirements.txt

# c:\Python\bookbuild-main\bookbuild_src\
# venvironment\Scripts\activate
# python manage.py export_ebook --book 1


# ===============================================================================
class EbookWriter:

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

            print("writing cover") if self.verbose else None
            html_destination = os.path.join(
                self.BOOK_BASE_DIR, "Add2Epub", "OEBPS/001_cover.html"
            )
        elif component_type == "chapter" and chapter:
            top5 = BookQueries.get_chapter_top5(chapter=chapter)
            ctx.update({"chapter": chapter, "top5": top5})

            if BookQueries.chapter_has_sections(chapter=chapter):
                html_path_list = [
                    settings.BASE_DIR,
                    "templates",
                    "ebook_exporter",
                    self.book.book_type,
                    "sectionBase.html",
                ]
                sections = []
                for section in BookQueries.get_all_chapter_sections(chapter):
                    subsections = BookQueries.get_section_list_subsections(section)
                    sections.append(
                        {"obj": section, "subsections": subsections,}
                    )
                ctx.update({"sections": sections})

            html_destination = os.path.join(self.BOOK_BASE_DIR, "Add2Epub", chapter.src)
            # if the above is still a problem, consider putting decode everywhere, like below.
            # html_destination = os.path.join(self.BOOK_BASE_DIR, "Add2Epub", chapter.src.decode('utf-8')
        elif component_type == "contents":
            chapters_all = BookQueries.get_content_chapters(book=self.book)
            items = BookQueries.get_subsection_for_chapters(chapters=chapters_all)
            ctx.update({"items": items})

            contents_chapter = BookQueries.get_contents_chapter(book=self.book)
            html_destination = os.path.join(
                self.BOOK_BASE_DIR, "Add2Epub", contents_chapter.src
            )

        html_file = os.path.join(*html_path_list)
        if not os.path.exists(html_file):
            # Remove book type if is generic template that exists in all book types.
            html_path_list.pop(-2)
            html_file = os.path.join(*html_path_list)

        f = codecs.open(html_file, "r")
        template_html = f.read()
        template = Template(template_html)
        f = open(html_destination, "w", encoding="utf-8")
        f.write(template.render(ctx))
        # Add html filename to list of files to clean up.
        self.FILES_TO_DELETE.append(html_destination)

        return template.render(ctx)

    # -------------------------------------------------------------------------------
    def writeBook(self):
        """For some reason calling writeTOC() inside of buildNewEpub() makes the toc not work,
        but this is fine.
        """

        # NOTE: I build book from whatever images and html i can find in Add2Epub/OEBPS

        # by the time i get here, html and images should be ready.

        # Copy uploaded images from media root to
        # copyanything(MEDIA_ROOT, self.DESTINATION_MEDIA_PATH)
        # so url will be same.

        if self.get_assets:
            # Note: 555 tips does not have any aws buckets
            download_images_from_aws(verbose=self.verbose)
            download_static_from_aws(verbose=self.verbose)

        imageList = BookQueries.get_all_images(book=self.book)
        # make folder media
        if not os.path.exists(self.DESTINATION_MEDIA_PATH):
            os.makedirs(self.DESTINATION_MEDIA_PATH)

        # ... NOTE this is irrelevant for 555 tips
        # check the properties img_urls and map_img_urls in Chapter, Section, Subsection to see naming convention
        # all all are jpg except maps which are png
        # NOTE 2: we start with 'Upper Sukhumvit'
        if len(imageList) > 1:  # it prob has 1 img, the cover.
            for i in imageList:
                # NOTE using i.img.file always called online location and didn't work offline.
                local_location = os.path.join(settings.MEDIA_ROOT, str(i.img.name))
                copyanything(local_location, self.DESTINATION_MEDIA_PATH)
        else:
            for i in os.listdir(settings.MEDIA_ROOT + f"{os.sep}img{os.sep}"):
                copyanything(
                    settings.MEDIA_ROOT + f"{os.sep}img{os.sep}" + i,
                    self.DESTINATION_MEDIA_PATH,
                )

        for f in BookQueries.get_all_files(book=self.book):
            DESTINATION_FILE_PATH = os.path.join(
                self.BOOK_BASE_DIR, "Add2Epub", "OEBPS", f.file_type
            )
            if not os.path.exists(DESTINATION_FILE_PATH):
                os.makedirs(DESTINATION_FILE_PATH)
            local_location = os.path.join(
                settings.MEDIA_ROOT, "ebook_exporter", "static", f.filename
            )
            copyanything(local_location, DESTINATION_FILE_PATH)
        # end image and naming convention note

        self.writeComponent("cover")

        for c in BookQueries.get_chapters_except_contents(book=self.book):
            self.writeComponent(component_type="chapter", chapter=c)
        if self.book.book_type in ["CK", "TG"]:
            contents_chapter = BookQueries.get_contents_chapter(book=self.book)
            if contents_chapter is not None:
                self.writeComponent("contents")

        self.writeOPF()
        self.writeTOC()
        self.buildNewEpub(self.book.slugify_title())

        cleanUp(
            files_to_delete=self.FILES_TO_DELETE,
            folders_to_delete=self.FOLDERS_TO_DELETE,
        )

    # Prob will nevr need to edit or look at this crap below.
    # -------------------------------------------------------------------------------
    def __init__(self, language, book=None, get_assets=False, verbose=False):
        self.language = language
        self.book = BookQueries.get_book(pk=book.id or 1,language=language)

        self.CSS_SNIPPET = ""
        for f in BookQueries.get_all_files(book=self.book):
            self.CSS_SNIPPET += (
                '<link href="%s" rel="stylesheet" type="text/css"/>' % f.relative_url
            )
        self.CSS_SNIPPET += (
            '<link href="css/stylesheet_custom.css" rel="stylesheet" type="text/css"/>'
        )

        self.get_assets = (
            get_assets  # whether or not to download images, css, etc from aws
        )

        self.verbose = verbose  # whether or not to log what's up on console

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
            "identifier": self.book.isbn or self.book.title,
            "creator": self.book.author_string,
            # "publisher": "Team Kaffeeklatsch",
            "date": time.strftime("%Y-%m-%d"),
            "language": self.language,
            "subject": self.book.subject or "",
            "description": self.book.description or "",
            "format": "0 pages",
            "type": "Text",
            "rights": "All rights reserved",
        }

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
            # "publisher",
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

        for dirname, media_type in {
            "css": "text/css",
            "fonts": "application/vnd.ms-opentype",
            "images": "image/jpeg",
        }.items():
            this_index = 0
            this_dir = os.path.join(self.BOOK_BASE_DIR, "Add2Epub", "OEBPS", dirname)
            
            # Recursively walk the directory to get all files, preserving nested paths
            files_to_process = []
            for root, dirs, files in os.walk(this_dir):
                for f in files:
                    # Get relative path from this_dir to the file
                    rel_path = os.path.relpath(os.path.join(root, f), this_dir)
                    files_to_process.append(rel_path)
            
            for f in files_to_process:
                this_index += 1
                # Use forward slashes for the href path (EPUB standard)
                href_path = f.replace(os.sep, '/')
                opf_str += (
                    "<item href='OEBPS/"
                    + dirname
                    + "/"
                    + href_path
                    + "' id = '"
                    + dirname[0]
                    + str(this_index)
                    + "' media-type='"
                    + media_type
                    + "'/>"
                )
        print(f"opf_str with pics:\n{opf_str}") if self.verbose else None

        if self.book.cover:
            cover_filename = f"media{os.sep}" + self.book.cover.get_file_name()
        else:
            cover_filename = f"images{os.sep}cover.jpg"
        opf_str += (
            "<item href='OEBPS/"
            + cover_filename
            + "' id = 'cover-image' media-type='image/jpeg'/>"
        )

        # incude cover html
        opf_str += "<item href='OEBPS/001_cover.html' id='HTML0' media-type='application/xhtml+xml'/>"
        spinelist.append("HTML0")

        for c in BookQueries.get_all_chapters(book=self.book):
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

        print("done writing everyhting?") if self.verbose else None

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

        for c in BookQueries.get_all_chapters(book=self.book):
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
            compress(newBookDir, book_dir)

            # 5. then change from zip to epub
            os.rename(
                os.path.join(self.BOOK_BASE_DIR, (thisTitle + ".zip")),
                os.path.join(self.BOOK_BASE_DIR, (thisTitle + ".epub")),
            )

            # 6. remove old folder
            cleanUp(folders_to_delete=[book_dir])
