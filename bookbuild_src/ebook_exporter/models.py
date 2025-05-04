import os
import re

# import requests

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.core.files import File
from django.conf import settings
from django.template.defaultfilters import slugify
from .model_enum import (
    FileTypeChoices,
    BookTypeChoices,
    LanguageTypeChoices,
    MediaTypeChoices,
    ChapterTypeChoices,
    FooterDetailChoices,
)
from django.db import transaction  # Import transaction for atomic operations
from translations.models import Translatable
from translations.querysets import TranslatableQuerySet
# MTDICT = [
#     ("jpg", "image/jpeg"),
#     ("html", "application/xhtml+xml"),
#     ("dtbncx", "application/x-dtbncx+xml"),
#     ("css", "text/css"),
#     ("vnd", "application/vnd.ms-opentype"),
# ]
# HEADERS = {
#     "User-agent": "Mozilla/5.0 (X11; U; Linux i686; de; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1"
# }
# ---------------------------------------------------------------------------
def atEnd(obj, field, objlist):
    # Terrible name i want to delete.

    return set_order_last(obj, field, objlist)


def set_order_last(obj, field, objlist):
    """For object w/ order or playOrder, puts at end by default.
    Here bc a few models do this.
    """

    currentOrder = getattr(obj, field)
    if currentOrder == 0:
        cnt = len(objlist)
        if cnt < 1:
            # If this is first object, make it 1.
            setattr(obj, field, 1)
        else:
            # make it last item, if no play order is specified.
            last = objlist[-1]
            lastOrder = getattr(last, field)
            setattr(obj, field, (lastOrder + 1))


def sequentialize_play_order(obj):

    # playOrder MUST BE SEQUENTIAL FOR toc.ncx.
    # If playOrder number is taken, Inserts a chapter obj desired position,
    # pushing all other indices up.
    try:
        dupelist = obj.__class__.objects.filter(
            book=obj.book, playOrder=obj.playOrder
        ).exclude(pk=obj.pk)
        if len(dupelist) > 0:
            # playOrder exists, push everything up.
            chapts = list(
                obj.__class__.objects.filter(
                    book=obj.book, playOrder__gte=obj.playOrder
                ).exclude(pk=obj.pk)
            )
            indices = list(
                range(obj.playOrder + 1, (obj.playOrder + (len(chapts)) + 1))
            )
            zipped = list(zip(indices, chapts))

            for tup in zipped:
                obj = tup[1]
                obj.playOrder = int(tup[0])
                # should not return self, but just in case, to avoid infinite loop:
                if obj.pk != obj.pk:
                    obj.save()
    except:
        # playOrder doesn't exist yet, all is good.
        pass


def make_src_file_name(obj):
    """Makes a filename for html, based on title.
    Don't save in this function, will be called @ save.
    """
    base_str = "OEBPS/0"
    # base_str = f"OEBPS{os.sep}0"
    if obj.playOrder < 10:
        base_str += "0"
    base_str += str(obj.playOrder) + "_"
    title = re.sub(r"[^\w]", "", obj.title.replace(" ", "").lower())
    base_str += title + ".html"
    return base_str


def replace_caps(caps_str):
    if caps_str.isupper():
        caps_str = caps_str.lower()
    return caps_str


def standardize_text_breaks(text):
    line_break = "\r\n"
    # Replace 3 or more consecutive line breaks with 1 line break
    text = re.sub(f"({re.escape(line_break)}){{3,}}", line_break, text)
    # Replace 2 consecutive line breaks with 1 line break
    text = re.sub(f"({re.escape(line_break)}){{2}}", line_break, text)
    # Replace all single line breaks with 2 line breaks
    text = text.replace(line_break, line_break * 2)
    return text

def create_translation_instance(instance, language="de"):
    """
    Take the source instance and copies text from all translatable fields fo that instance, to have a base for replacing.
    Example: Book obj with title can be translated. if language is 'sp' we will have an entry for sp for the obj, 
    but the actual test will be text will be the same as the origional object (until someone logs in to admin and changes it)
    """
    from django.contrib.contenttypes.models import ContentType
    from translations.models import Translation

    continent_ct = ContentType.objects.get_for_model(type(instance))
    translatable_fields = instance._get_translatable_fields_names()
    for f in translatable_fields:
        base_content = getattr(instance, f)
        if base_content is not None:
            Translation.objects.create(
                content_type=continent_ct,
                object_id=instance.pk,
                field=f,
                language=language,
                text=getattr(instance, f),
            )


# ===============================================================================
class Person(models.Model):
    """Could be a person, could be a business, etc.
    This is cleaned up and how will be presented in list of contributors or photographers in back.
    """

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    # If it's a company, just use lname. That's how it's being ordered.
    lname = models.CharField(max_length=200)
    fname = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    # ---------------------------------------------------------------------------

    def __str__(self):
        if self.fname:
            return "%s %s" % (self.fname, self.lname)
        else:
            return "%s" % (self.lname)

    # ---------------------------------------------------------------------------
    class Meta:
        abstract = True


# ===============================================================================
class Author(Person):

    order = models.IntegerField(default=0)

    # ---------------------------------------------------------------------------
    class Meta:
        ordering = ["lname", "order"]


# ===============================================================================
class StaticFile(models.Model):
    """File such as CSS that book might need.
    """

    # file type will also be the name of the dir.
    file_type = models.CharField(
        max_length=200, choices=FileTypeChoices.CHOICES, default="css"
    )
    upload = models.FileField(upload_to="exporter/static/")

    # ---------------------------------------------------------------------------
    def __str__(self):
        return "%s: %s" % (self.file_type, self.upload.name)

    # ---------------------------------------------------------------------------
    @property
    def relative_url(self):
        """url to use in ebook.
        """
        # i thik this doesn't need os.sep?
        return self.file_type + "/" + self.filename

    # ---------------------------------------------------------------------------
    @property
    def filename(self):
        # return self.upload.name.split(os.sep)[-1]
        return self.upload.name.split("/")[-1]


# ===============================================================================
class Image(models.Model):
    """Image that I need to track and give credit for.
    """

    caption = models.CharField(max_length=200, null=True, blank=True)
    img = models.ImageField(upload_to=os.path.join("img"))

    # does copyright need to be cited? False if free stock image.
    needsCitation = models.BooleanField(default=False)
    # Is it in the book hard-coded? ie does it need tobe copied,
    # but will thie relationship not be found via recipes, sections, or chapters?
    book = models.ForeignKey("Book", null=True, blank=True, on_delete=models.SET_NULL)

    # ---------------------------------------------------------------------------
    def image_tag(self):
        path = os.path.join(settings.MEDIA_URL, str(self.img))
        return mark_safe('<img src="%s" height="100" />' % (path))

    image_tag.short_description = "Image"

    # ---------------------------------------------------------------------------
    def __str__(self):

        strname = ""
        try:
            strname += str(self.img.url).split("/img/")[-1]
        except:
            strname += str(self.img.url)
        strname += " (%s)" % (str(self.pk))

        return strname

    # ---------------------------------------------------------------------------
    def upload_to_s3(self):
        """Should be automatic for all new images.
        Just doing this for existing images.
        """
        # filename = self.img.name # I think this gave me th double img.
        # filename = str(self.img.url).split("/img/")[-1]
        filename = str(self.img.url).split("/")[-1]
        try:
            self.img.save(filename, File(open("static/media/img/" + filename, "rb")))
            self.save()
        except IOError as e:
            print("problem uploading %s: %s" % (str(self.img.name), str(e)))

    # ---------------------------------------------------------------------------
    def get_file_name(self):
        # duh this removes extension
        # m = re.search('img/(.+?)\.', self.img.name)
        # return m.group(1)
        return self.img.name.split("/")[-1]

    # ---------------------------------------------------------------------------
    @property
    def relative_url(self):
        """url to use in ebook.
        """
        last_name = self.img.name.split("/")[-1]
        return "media/" + last_name


# ===============================================================================
class BookManager(models.Manager):

    # ---------------------------------------------------------------------------
    def get_images(self, book):
        """Gets images that are related by subsection, section,
        or by book field in image model.
        """
        images = list(book.image_set.all())
        if book.cover:
            images.append(book.cover)
        # for mod in [Subsection, Chapter]:
        for mod in [Chapter]:
            for obj in mod.objects.filter(book=book):
                if hasattr(obj, "img") and obj.img:
                    images.append(obj.img)
                if hasattr(obj, "img_lower") and obj.img_lower:
                    images.append(obj.img_lower)
        return images


# ===============================================================================
class Book(Translatable):
    """Should this be ABS or what?
    """

    book_type = models.CharField(
        max_length=200,
        choices=BookTypeChoices.CHOICES,
        default=BookTypeChoices.NONFICTION,
    )
    title = models.CharField(max_length=200)
    cover = models.ForeignKey(
        Image, null=True, blank=True, related_name="bookcover", on_delete=models.PROTECT
    )
    author = models.ManyToManyField(Author, blank=True)

    files = models.ManyToManyField(StaticFile, blank=True)

    # Metadata for toc.ncx and content.opf
    language = models.CharField(
        max_length=200,
        choices=LanguageTypeChoices.CHOICES,
        default=LanguageTypeChoices.ENGLISH,
    )
    isbn = models.CharField(
        max_length=200, null=True, blank=True, help_text="EX: isbn-000-0-000-00000-0"
    )
    subject = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="/ separated html. Example: 'COOKING / Courses &amp; Dishes / General'",
    )
    description = models.TextField(null=True, blank=True)

    # objects = BookManager()
    # NOTE have to do this if you want to keep your custom manager
    objects = BookManager.from_queryset(TranslatableQuerySet)()
  

    class TranslatableMeta:
        fields = ['title', 'description']

    # ---------------------------------------------------------------------------

    def __str__(self):
        return "%s" % (self.title)

    # ---------------------------------------------------------------------------
    def sequentialize(self):
        """playOrder MUST BE SEQUENTIAL FOR toc.ncx.
        But I reserve position 1 for the cover.
        This makes playOrder of all chapter objects sequential without missing an index
        """
        po_count = self.chapter_set.all().count()
        chapters = list(self.chapter_set.all().order_by("playOrder"))
        indices = list(range(2, po_count + 1))
        zipped = list(zip(indices, chapters))
        for tup in zipped:
            obj = tup[1]
            obj.playOrder = int(tup[0])
            obj.save()

    # ---------------------------------------------------------------------------
    def slugify_title(self):
        """sligify title so i can name file safely.
        """
        return slugify(self.title)

    # ---------------------------------------------------------------------------
    @property
    def author_string(self):
        authors = [str(x) for x in self.author.all()]
        return ", ".join(authors)

    # ---------------------------------------------------------------------------
    @property
    def author_html(self):
        authors = [(x.fname + " " + x.lname) for x in self.author.all()]
        return "&amp; ".join(authors)

    # ---------------------------------------------------------------------------
    class Meta:
        ordering = [
            "title",
        ]


# Neighborhood will become Chapter, just needs Title and order (playOrder)
# the following is what is happens per chapter:
# # - pre content (i forgot what that means where is this written?)
# # - priority 5 items, regardless of which section the item is in
# # - then each section. Section order matters
# # # # # - blobs are by section, orderd by priority,
#              it looks like I wrote "content doesn't matter" but i can't read it. Maybe category doesn't matter?
#
#
# Categories only matter because of section. blabs should have section.

# ===============================================================================
class Chapter(Translatable):
    """Book components, more generally, but often specfically in form of chapters.
        Standard order will be:
        Cover, Copyright, and then maybe Chapter 1, or Introduction, so on and so forth
        until maybe an index and then the back cover at the very end.
        This is used to construct the toc.ncx as well as content.opf, so you
        only need to specify info once.
        Summary: ill not ALWAYS be a chapter, but will often be a chapter, so is named as such.
    """

    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    # For toc.ncx
    title = models.CharField(max_length=200)
    # subtitle =  models.CharField(max_length=200, null=True, blank=True)
    display_title = models.BooleanField(default=True)
    # navPoint_id =  models.CharField(max_length=200, unique = True)
    playOrder = models.IntegerField(default=2, validators=[MinValueValidator(2)])
    intro = models.TextField(null=True, blank=True)

    # When and where am I going to sync src w/ actual file names?
    # Maybe I'll write something that looks for mismatches? Makes sure all chapters correspond to real files?
    # See if any files can't be found as chapters?
    src = models.CharField(max_length=200, null=True, blank=True)

    # For content.opf
    media_type = models.CharField(
        max_length=200,
        choices=MediaTypeChoices.CHOICES,
        default=MediaTypeChoices.MEDIA_HTML,
    )
    chapter_type = models.CharField(
        max_length=200,
        choices=ChapterTypeChoices.CHOICES,
        default=ChapterTypeChoices.CHAPTER_CH,
    )

    bodyText = models.TextField(null=True, blank=True)

    class TranslatableMeta:
        fields = ['title', 'intro','bodyText']

    # ---------------------------------------------------------------------------

    def __str__(self):
        return "%s. %s " % (self.playOrder, self.title)

    # ---------------------------------------------------------------------------
    class Meta:
        ordering = [
            "playOrder",
        ]
        unique_together = (("title", "book"), ("book", "src"))

    # ---------------------------------------------------------------------------
    @property
    def chapter_url(self):
        return str(self.src).replace("OEBPS/", "")

    @property
    def title_lower_snake(self):
        # snake case
        # & is a problem
        #title = self.title
        # Have to use .translations.content_object to get origional title
        t =  self.translations.first()
        title = t.content_object.title
        return title.lower().replace(" ", "_").replace("&", "and")

    @property
    def img_url(self):
        # base_name_start = f"{self.title_lower_snake}_title__"
        base_name_start = f"{self.title_lower_snake}__"
        base_name_end = ".jpg"
        pattern = re.compile(
            f"{re.escape(base_name_start)}.*{re.escape(base_name_end)}", re.IGNORECASE
        )
        try:
            img_pattern_files = os.listdir(
                f"{settings.IMG_DIR}{os.sep}{self.title_lower_snake}"
            )
            matching_files = [
                f"images{os.sep}{self.title_lower_snake}{os.sep}{filename}"
                for filename in img_pattern_files
                if pattern.match(filename)
            ]
            return matching_files[0]
        except (FileNotFoundError, IndexError):
            return []

    @property
    def map_img_url(self):
        base_name_start = f"{self.title_lower_snake}_map__"
        base_name_end = ".png"
        pattern = re.compile(
            f"{re.escape(base_name_start)}.*{re.escape(base_name_end)}"
        )  # Construct the regex pattern
        try:
            img_pattern_files = os.listdir(
                f"{settings.IMG_DIR}{os.sep}{self.title_lower_snake}"
            )
            matching_files = [
                f"images{os.sep}{self.title_lower_snake}{os.sep}{filename}"
                for filename in img_pattern_files
                if pattern.match(filename)
            ]
            return matching_files[0]
        except (FileNotFoundError, IndexError):
            return []

    # ---------------------------------------------------------------------------
    def save(self, *args, **kwargs):
        # default playOrder is 0, but playOrder in toc.ncx should be 1 indexed
        set_order_last(
            self,
            "playOrder",
            list(Chapter.objects.filter(book=self.book).order_by("playOrder")),
        )

        # playOrder MUST BE SEQUENTIAL FOR toc.ncx.
        sequentialize_play_order(self)

        if not self.src:
            self.src = make_src_file_name(self)

        return super(Chapter, self).save(*args, **kwargs)


# Category / Section becomes this
# # ===============================================================================
class Section(Translatable):

    title = models.CharField(max_length=200)
    order = models.PositiveSmallIntegerField(null=True, blank=True)
    main_text = models.TextField(null=True, blank=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.PROTECT)
    # Image. Can be blank/null, but I prefer not to.
    # img = models.ForeignKey(Image, null=True, blank=True, on_delete=models.PROTECT)

    # Is this related to a chapter in the book?
    # Cookbook structure: Section should be a chapter, but chapter might not be a section.
    # New travel structure: section is under chapter, in hierarchy

    # ---------------------------------------------------------------------------

    def __str__(self):
        return "%s" % (self.title)

    @property
    def title_lower_snake(self):
        # snake case
        # & is a problem
        #title = self.title
        # Have to use .translations.content_object to get origional title
        t =  self.translations.first()
        title = t.content_object.title
        return title.lower().replace(" ", "_").replace("&", "and")

    @property
    def img_url(self):
        base_name_start = f"{self.title_lower_snake}__"
        base_name_end = ".jpg"
        pattern = re.compile(
            f"{re.escape(base_name_start)}.*{re.escape(base_name_end)}", re.IGNORECASE
        )
        image_dir = f"{settings.IMG_DIR}{os.sep}{self.chapter.title_lower_snake}"
        try:
            img_pattern_files = os.listdir(image_dir)
            matching_files = [
                f"images{os.sep}{self.chapter.title_lower_snake}{os.sep}{filename}"
                for filename in img_pattern_files
                if pattern.match(filename)
            ]
            return matching_files[0]
        except (FileNotFoundError, IndexError):
            return []

    # ---------------------------------------------------------------------------
    class Meta:
        ordering = [
            "chapter",
            "order",
        ]

    class TranslatableMeta:
        fields = ['title', 'main_text']

# # ===============================================================================
class Subsection(Translatable):
    """Formerly Blob"""

    title = models.CharField(max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(null=True, blank=True)
    section = models.ForeignKey(Section, on_delete=models.PROTECT)
    priority = models.PositiveSmallIntegerField(null=True, blank=True)
    category_text = models.CharField(null=True, blank=True, max_length=200)
    main_text = models.TextField(null=True, blank=True)
    footer_text = models.TextField(null=True, blank=True)

    # footer_bts_text = models.TextField(null=True, blank=True)
    # footer_mrt_text = models.TextField(null=True, blank=True)
    # footer_kanalboot_text = models.TextField(null=True, blank=True)
    # footer_flussboot_text = models.TextField(null=True, blank=True)
    # footer_address_text = models.TextField(null=True, blank=True)
    # footer_address_link = models.URLField(null=True, blank=True)

    # Image. Can be blank/null, but I prefer not to.
    # img = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    # img_lower = models.ForeignKey(
    #     Image, null=True, blank=True, related_name="lower", on_delete=models.SET_NULL
    # )
    # halfpage = models.BooleanField(default=False)
    # text = models.TextField(null=True, blank=True)

    # ---------------------------------------------------------------------------

    def __str__(self):
        return "%s" % (self.title)


    class TranslatableMeta:
        fields = ['title', 'category_text','main_text','footer_text']

    @property
    def anchor_id(self):
        return f"subsection-{self.pk}"

    @property
    def internal_url(self):
        chapter_url = self.section.chapter.chapter_url
        return f"{chapter_url}#{self.anchor_id}"

    @property
    def title_lower_snake(self):
        # snake case
        # & is a problem
        #title = self.title
        # Have to use .translations.content_object to get origional title
        t =  self.translations.first()
        title = t.content_object.title
        return title.lower().replace(" ", "_").replace("&", "and")

    @property
    def img_url(self):
        base_name_start = f"{self.title_lower_snake}__"
        base_name_end = ".jpg"
        pattern = re.compile(
            f"{re.escape(base_name_start)}.*{re.escape(base_name_end)}", re.IGNORECASE
        )
        try:
            img_pattern_files = os.listdir(
                f"{settings.IMG_DIR}{os.sep}{self.section.chapter.title_lower_snake}"
            )
            matching_files = [
                f"images{os.sep}{self.section.chapter.title_lower_snake}{os.sep}{filename}"
                for filename in img_pattern_files
                if pattern.match(filename)
            ]
            return matching_files[0]
        except (FileNotFoundError, IndexError):
            return []

    def parse_footer_text(self):
        if not self.footer_text:
            return

        # Create transport_mapping dynamically from FooterDetailChoices
        transport_mapping = {
            choice[1].upper(): choice[0]
            for choice in FooterDetailChoices.CHOICES
            if choice[0]
            not in [FooterDetailChoices.WEB, FooterDetailChoices.GOOGLE_MAPS]
        }

        # Use regex to find the URL and the text for the address
        address_pattern = r'<a\s+href\s*=\s*["\'](https?://[^"\']+)["\']\s*>(.*?)<\/a>'
        address_matches = re.findall(address_pattern, self.footer_text)
        # Create FooterTransport for the address
        for url, address in address_matches:
            address_type = FooterDetailChoices.WEB  # Default type for address
            if "www.google.com/maps/" in url:
                address_type = (
                    FooterDetailChoices.GOOGLE_MAPS
                )  # Set type to GOOGLE_MAPS if URL matches
            # Check if the record already exists
            if not FooterDetail.objects.filter(
                subsection=self, type=address_type
            ).exists():
                FooterDetail.objects.create(
                    subsection=self, type=address_type, text=address, url=url
                )

        # Use regex to find transport types and their corresponding texts
        transport_keys = "|".join(transport_mapping.keys())  # Join keys with '|'
        # Updated regex pattern to be case insensitive
        transport_pattern = (
            rf"({transport_keys}):\s*([^;\r\n]+)"  # Use raw string for regex
        )
        transport_matches = re.findall(
            transport_pattern, self.footer_text, re.IGNORECASE
        )

        # Create FooterTransport for each transport type
        for transport_type, text in transport_matches:
            mapped_type = transport_mapping[transport_type.upper()]
            if not FooterDetail.objects.filter(
                subsection=self, type=mapped_type
            ).exists():
                FooterDetail.objects.create(
                    subsection=self, type=mapped_type, text=text.strip()
                )
        if len(transport_matches) > 0 or len(address_matches) > 0:
            print(f"{self} {self.pk}")
            if len(transport_matches) > 0:
                print(f"transport_matches: {transport_matches}")
            if len(address_matches) > 0:
                print("address_matches:", address_matches)

    # ---------------------------------------------------------------------------
    class Meta:
        ordering = [
            "section",
            "priority",
            "order",
        ]

#     # ---------------------------------------------------------------------------
#     def download_image(self):
#         if not self.recipe_img_url:
#             print("Can't, no recipe_img_url.")
#             return
#         imagename = self.recipe_img_url.split("/")[-1]
#         print("\n\n---About to get %s for %s" % (str(self.recipe_img_url), str(self)))
#         with open(imagename, "wb") as f:
#             f.write(requests.get(self.recipe_img_url, headers=HEADERS).content)
#             print("downloaded")
#         image = Image()
#         image.img.save(imagename, File(open(imagename, "rb")))
#         image.save()
#         self.img = image
#         self.save()
#         if os.path.exists(imagename):
#             os.remove(imagename)
#             print("%s deleted" % imagename)

#     # ---------------------------------------------------------------------------
#     def clean_caps(self, fieldname):
#         if hasattr(self, fieldname):
#             dirty = getattr(self, fieldname)
#             textlist = dirty.split()
#             new = []
#             for t in textlist:
#                 clean = replace_caps(t)
#                 new.append(clean)
#             new_field = " ".join(new)
#             setattr(self, fieldname, new_field)
#             return new_field
#         else:
#             print("no field")
#             # self.save()

#     # ---------------------------------------------------------------------------
#     @property
#     def internal_url(self):
#         """Gets link to self in case other recipe wants to link ot it
#         """
#         section_url = str((self.section.chapter.src)).replace("OEBPS/", "")
#         recipe_url = section_url + ("#subsection-" + str(self.pk))
#         return recipe_url


class FooterDetail(Translatable):

    subsection = models.ForeignKey(Subsection, on_delete=models.CASCADE, related_name="footer_details")
    type = models.CharField(
        max_length=7,
        choices=FooterDetailChoices.CHOICES,
        default=FooterDetailChoices.BTS,
    )
    text = models.CharField(max_length=200)
    mins = models.PositiveSmallIntegerField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    # class TranslatableMeta:
    #     fields = ['title', 'description']

    def __str__(self):
        return "%s" % (self.text)
    
    @property
    def icon_img_png(self):
        # if self.type not in [FooterDetailChoices.WEB, FooterDetailChoices.GOOGLE_MAPS]:
        #     return f"images/icons/png/{self.type}.png"
        return f"images/icons/png/{self.type}.png"