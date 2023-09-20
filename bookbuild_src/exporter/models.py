import os
import re
import requests

from bs4 import BeautifulSoup

from django.core.validators import MinValueValidator
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.core.files import File
from django.conf import settings
from django.template.defaultfilters import slugify

from ordered_model.models import OrderedModel

MTDICT = [
        ("jpg", "image/jpeg"),
        ("html", "application/xhtml+xml"),
        ("dtbncx", "application/x-dtbncx+xml"),
        ("css", "text/css"),
        ("vnd", "application/vnd.ms-opentype"),
]
HEADERS = {'User-agent': 'Mozilla/5.0 (X11; U; Linux i686; de; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'}
#---------------------------------------------------------------------------
def atEnd(obj, field, objlist):
    """For object w/ order or playOrder, puts at end by default.
    Here bc a few models do this.
    """

    currentOrder = getattr(obj, field)
    if currentOrder == 0:
        cnt = len(objlist)
        if cnt < 1:
            #If this is first object, make it 1.
            setattr(obj, field, 1)
        else:
            #make it last item, if no play order is specified.
            last = objlist[-1]
            lastOrder = getattr(last, field)
            setattr(obj, field, (lastOrder + 1))
            
            

def replace_caps(caps_str):
    if caps_str.isupper():
        caps_str = caps_str.lower()
    return caps_str


#===============================================================================
class Person(models.Model):
    """Could be a person, could be a business, etc.
    This is cleaned up and how will be presented in list of contributors or photographers in back.
    """
    user = (models.ForeignKey(
            User, null=True, blank=True, on_delete=models.SET_NULL)
            )
    #If it's a company, just use lname. That's how it's being ordered.
    lname =  models.CharField(max_length=200)
    fname =  models.CharField(max_length=200, null = True, blank = True)
    description = models.TextField(null = True, blank = True)

    url = models.URLField(null=True, blank=True)
    #social media links
    facebook = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    youtube = models.URLField(null=True, blank=True)

    #---------------------------------------------------------------------------
    def __str__(self):
        if self.fname:
            return "%s %s" % (self.fname, self.lname)
        else:
            return "%s" % (self.lname)

    #---------------------------------------------------------------------------
    class Meta:
        abstract = True

    #---------------------------------------------------------------------------
    @property
    def credit_contrib_url(self):
        chap = Chapter.objects.get(title = "Contributors")
        section_url = str(chap.src).replace("OEBPS/", "")

        if self.description:
            url_str = section_url + "#contributor-" + str(self.pk)
        else:
            url_str = section_url + "#photographer-" + str(self.pk)

        return url_str


#===============================================================================
class Author(Person):

    order = models.IntegerField(default = 0)

    #---------------------------------------------------------------------------
    class Meta:
        ordering = ['lname', 'order']

#===============================================================================
class Contributor(Person):
    pass

    #---------------------------------------------------------------------------
    class Meta:
        ordering = ['lname',]

#===============================================================================
class StaticFile(models.Model):
    """File such as CSS that book might need.
    """
    FONT = 'fonts'
    IMG = 'images'
    CSS = 'css'
    
    FILE_TYPE_CHOICES = [
            (FONT, FONT),
            (IMG, IMG),
            (CSS, CSS),
    ]    
    # file typw will also be the name of the dir.
    file_type = models.CharField(max_length=200, choices=FILE_TYPE_CHOICES, default="css")
    upload = models.FileField(upload_to='bookbuild/static/')

    #---------------------------------------------------------------------------
    def __str__(self):
        return "%s: %s" % (self.file_type, self.upload.name)

    #---------------------------------------------------------------------------
    @property
    def relative_url(self):
        """url to use in ebook.
        """
        return self.file_type + "/" + self.filename
    #---------------------------------------------------------------------------
    @property
    def filename(self):
        return self.upload.name.split("/")[-1]  
                
#===============================================================================
class Image(models.Model):
    """Image that I need to track and give credit for.
    """
    caption = models.CharField(max_length=200, null=True, blank = True)
    img = models.ImageField(upload_to=os.path.join('img'))

    credit = models.ForeignKey(Contributor, null=True, blank = True, on_delete=models.PROTECT)
    # does copyright need to be cited? False if free stock image.
    needsCitation = models.BooleanField(default=False)
    #Is it in the book hard-coded? ie does it need tobe copied,
    # but will thie relationship not be found via recipes, sections, or chapters?
    book = models.ForeignKey("Book", null=True, blank = True, on_delete=models.SET_NULL)

    #---------------------------------------------------------------------------
    def image_tag(self):
        path = os.path.join(settings.MEDIA_URL, str(self.img))
        return mark_safe('<img src="%s" height="100" />' % (path))
    image_tag.short_description = 'Image'

    #---------------------------------------------------------------------------
    def __str__(self):
        
        if self.credit:
            strname = "%s: " % (str(self.credit)) 
        else:
             strname=""  
        
        try:
            strname += str(self.img.url).split("/img/")[-1]
        except:
            strname += str(self.img.url)
        strname += " (%s)" % (str(self.pk))

        return strname

    #---------------------------------------------------------------------------
    def upload_to_s3(self):
        """Should be automatic for all new images.
        Just doing this for existing images.
        """
        #filename = self.img.name # I think this gave me th double img.
        #filename = str(self.img.url).split("/img/")[-1]
        filename = str(self.img.url).split("/")[-1]
        try:
            self.img.save(filename, File(open('static/media/img/'+ filename, 'rb')))
            self.save()
        except IOError as e:
            print("problem uploading %s: %s"% (str(self.img.name), str(e)))

    #---------------------------------------------------------------------------
    def get_file_name(self):
        #duh this removes extension
        # m = re.search('img/(.+?)\.', self.img.name)
        # return m.group(1)
        return self.img.name.split("/")[-1]
    
    #---------------------------------------------------------------------------
    class Meta:
        ordering = ('credit',)

    #---------------------------------------------------------------------------
    @property
    def relative_url(self):
        """url to use in ebook.
        """
        last_name = self.img.name.split("/")[-1]
        return "media/" + last_name


#===============================================================================
class BookManager(models.Manager):

    #---------------------------------------------------------------------------
    def get_images(self, book):
        """Gets images that are related by subsection, section,
        or by book field in image model.
        """
        images = list(book.image_set.all())
        if book.cover:
            images.append(book.cover)
        for mod in [Subsection, Chapter]:
            for obj in mod.objects.filter(book=book):
                if hasattr(obj, "img") and obj.img:               
                    images.append(obj.img)
                if hasattr(obj, "img_lower") and obj.img_lower:
                    images.append(obj.img_lower)   
        return images

#===============================================================================
class Book(models.Model):
    """Should this be ABS or what?
    """
    COOKBOOK = 'CK'
    TRAVELGUIDE = "TG"
    NONFICTION = 'NF'
    BOOK_TYPE_CHOICES = [
            (COOKBOOK, "cookbook"),
            (NONFICTION, "nonfiction"),
            (TRAVELGUIDE, "travelguide"),
    ]
    
    ENGLISH = "EN"
    GERMAN = "DE"
    BOOK_LANGUAGE_CHOICES = [
            (ENGLISH, "English"),
            (GERMAN , "German"),
    ]    
    
    book_type = models.CharField(max_length=200, choices=BOOK_TYPE_CHOICES, default=NONFICTION)
    title =  models.CharField(max_length=200)
    cover = models.ForeignKey(Image, null=True, blank=True, related_name="bookcover", on_delete=models.PROTECT)
    author = models.ManyToManyField(Author, blank=True)
    
    files = models.ManyToManyField(StaticFile, blank=True)
    
    # Metadata for toc.ncx and content.opf
    language =  models.CharField(max_length=200, choices=BOOK_LANGUAGE_CHOICES, default=ENGLISH)
    isbn =  models.CharField(max_length=200, null=True, blank=True, help_text="EX: isbn-000-0-000-00000-0")
    subject = models.CharField(max_length=200, null=True, blank=True, help_text="/ separated html. Example: 'COOKING / Courses &amp; Dishes / General'")
    description = models.TextField(null=True, blank=True)
    
    objects = BookManager()

    #---------------------------------------------------------------------------
    def __str__(self):
        return "%s" % (self.title)

    #---------------------------------------------------------------------------
    def sequentialize(self):
        """playOrder MUST BE SEQUENTIAL FOR toc.ncx.
        But I reserve position 1 for the cover.
        This makes playOrder of all chapter objects sequential without missing an index
        """
        po_count = (self.chapter_set.filter(publish=True).count())
        chapters = list(self.chapter_set.filter(publish=True).order_by("playOrder"))
        indices = list(range(2, po_count+1))
        zipped = list(zip(indices, chapters))
        for tup in zipped:
            obj = tup[1]
            obj.playOrder = int(tup[0])
            obj.save()

    #---------------------------------------------------------------------------
    def slugify_title(self):
        """sligify title so i can name file safely.
        """
        return slugify(self.title)
    #---------------------------------------------------------------------------
    @property
    def author_string(self):
        authors = [str(x) for x in self.author.all()]
        return ", ".join(authors)
        
    #---------------------------------------------------------------------------
    @property
    def author_html(self):
        authors = [(x.fname + " " +  x.lname) for x in self.author.all()]
        return "&amp; ".join(authors)

    #---------------------------------------------------------------------------
    class Meta:
        ordering = ['title',]


#===============================================================================
class Chapter(models.Model):
    """Book components, more generally, but often specfically in form of chapters.
        Standard order will be:
        Cover, Copyright, and then maybe Chapter 1, or Introduction, so on and so forth
        until maybe an index and then the back cover at the very end.
        This is used to construct the toc.ncx as well as content.opf, so you
        only need to specify info once.
        Summary: ill not ALWAYS be a chapter, but will often be a chapter, so is named as such.
    """
    MEDIA_JPEG = 'jpg'
    MEDIA_HTML = 'html'
    MEDIA_DTBNCX = 'dtbncx'
    MEDIA_CSS = 'css'
    MEDIA_VND = 'vnd'
    
    MEDIA_TYPE_CHICES = [
            (MEDIA_JPEG, "image/jpeg"),
            (MEDIA_HTML, "application/xhtml+xml"),
            (MEDIA_DTBNCX, "application/x-dtbncx+xml"),
            (MEDIA_CSS, "text/css"),
            (MEDIA_VND, "application/vnd.ms-opentype"),
    ]

    book = models.ForeignKey(Book, null = True, blank = True, on_delete=models.PROTECT)
    # For toc.ncx
    title =  models.CharField(max_length=200)
    # subtitle =  models.CharField(max_length=200, null=True, blank=True)
    display_title = models.BooleanField(default=True)
    #navPoint_id =  models.CharField(max_length=200, unique = True)
    playOrder = models.IntegerField(default=2, validators=[MinValueValidator(2)])
    publish = models.BooleanField(default=True)

    # When and where am I going to sync src w/ actual file names?
    # Maybe I'll write something that looks for mismatches? Makes sure all chapters correspond to real files?
    # See if any files can't be found as chapters?
    src = models.CharField(max_length=200,blank = True)

    # For content.opf
    media_type = models.CharField(max_length=200, choices=MEDIA_TYPE_CHICES, default=MEDIA_HTML )

    bodyText = models.TextField(null = True, blank = True)

    #---------------------------------------------------------------------------
    def __str__(self):
        return "%s. %s " % (self.playOrder, self.title)

    #---------------------------------------------------------------------------
    class Meta:
        ordering = ['playOrder',]
        unique_together = (('title', 'book'), ('book', 'src'))

    #---------------------------------------------------------------------------
    @property
    def chapter_url(self):

        return str(self.src).replace("OEBPS/", "")


    #---------------------------------------------------------------------------
    def makeFileName(self):
        """Makes a filename for html, based on title.
        Don't save in this function, will be called @ save.
        """

        base_str = "OEBPS/0"
        if self.playOrder < 10:
            base_str +="0"
        base_str += str(self.playOrder) + "_"
        title = self.title.replace(" ", "").lower()
        base_str += title + ".html"

        return base_str

    #---------------------------------------------------------------------------
    def save(self, *args, **kwargs):

        #default playOrder is 0, but playOrder in toc.ncx should be 1 indexed
        atEnd(self, "playOrder", list(Chapter.objects.filter(book=self.book, publish=True).order_by("playOrder")))

        # playOrder MUST BE SEQUENTIAL FOR toc.ncx.
        # If playOrder number is taken, Inserts a chapter obj desired position,
        # pushing all other indices up.
        try:
            dupelist  = Chapter.objects.filter(book=self.book, publish=True, playOrder = self.playOrder).exclude(pk = self.pk)
            if len(dupelist) > 0:
                #playOrder exists, push everything up.
                chapts = list(Chapter.objects.filter(book=self.book, publish=True, playOrder__gte = self.playOrder).exclude(pk = self.pk))
                indices = list(range(self.playOrder+1, (self.playOrder + (len(chapts)) +1) ))
                zipped = list(zip(indices, chapts))

                for tup in zipped:
                    obj = tup[1]
                    obj.playOrder = int(tup[0])
                    #should not return self, but just in case, to avoid infinite loop:
                    if obj.pk != self.pk:
                        obj.save()
        except:
            # playOrder doesn't exist yet, all is good.
            pass
        
        if not self.src:
            self.src = self.makeFileName()

        super(Chapter, self).save()


#===============================================================================
class Section(models.Model):
    """Soups, starts/sides, etc.
    """

    title =  models.CharField(max_length=200)
    #Image. Can be blank/null, but I prefer not to.
    img = models.ForeignKey(Image, null = True, blank = True, on_delete=models.PROTECT)

    #Is this related to a chapter in the book?
    #Section should be a chapter, but chapter might not be a section.
    chapter = models.OneToOneField(Chapter, on_delete=models.PROTECT, null = True, blank = True)

    #---------------------------------------------------------------------------
    def __str__(self):
        return "%s" % (self.title)

    #---------------------------------------------------------------------------
    class Meta:
        ordering = ['title',]

    #---------------------------------------------------------------------------
    def save(self, *args, **kwargs):

        if self.chapter:
            if str(self.chapter.title) != str(self.title):
                self.chapter.title = self.title
                self.chapter.save()

        super(Section, self).save()


#===============================================================================
class Subsection(OrderedModel):
    """Formerly Recipe"""

    title =  models.CharField(max_length=200, blank = True)
    # If no contributor,is mine. Make sure this is true.
    
    #Image. Can be blank/null, but I prefer not to.
    img = models.ForeignKey(Image, null = True, blank = True, on_delete=models.SET_NULL)
    img_lower = models.ForeignKey(Image, null = True, blank = True, related_name="lower", on_delete=models.SET_NULL)

    #Note links ot book AND section. redundant, but make sit easier to get. maybe a bad idea.
    book = models.ForeignKey(Book, null = True, blank = True, on_delete=models.PROTECT)
    section = models.ForeignKey(Section, null = True, blank = True, on_delete=models.SET_NULL)
    order_with_respect_to = ('book', 'section',)
    halfpage = models.BooleanField(default=False)

    # Common Recipe Components
    text = models.TextField(null = True, blank = True)

    publish = models.BooleanField(default=True)

    #---------------------------------------------------------------------------
    def download_image(self):
        if not self.recipe_img_url:
            print("Can't, no recipe_img_url.")
            return
        imagename = self.recipe_img_url.split("/")[-1]
        print("\n\n---About to get %s for %s"%(str(self.recipe_img_url), str(self)))
        with open(imagename,'wb') as f:
            f.write(requests.get(self.recipe_img_url, headers=HEADERS).content)
            print("downloaded")
        image = Image()
        image.img.save(imagename,File(open(imagename, 'rb')))
        image.save()
        self.img = image
        self.save()
        print("saved")
        if os.path.exists(imagename):
            os.remove(imagename)
            print("%s deleted"%imagename)

    #---------------------------------------------------------------------------
    def clean_caps(self, fieldname):
        if hasattr(self, fieldname):
            dirty = getattr(self, fieldname)
            textlist = dirty.split()
            new = []
            for t in textlist:
                clean = replace_caps(t)
                new.append(clean)
            new_field = " ".join(new)
            setattr(self, fieldname, new_field )
            return new_field
        else:
            print("no field")
            #self.save()


    #---------------------------------------------------------------------------
    def __str__(self):
        return "%s" % (self.title)

    #---------------------------------------------------------------------------
    class Meta(OrderedModel.Meta):
        # ordering = ['title']
        pass

    #---------------------------------------------------------------------------
    @property
    def internal_url(self):
        """Gets link to self in case other recipe wants to link ot it
        """
        section_url = str((self.section.chapter.src)).replace("OEBPS/", "")
        recipe_url = (section_url + ("#subsection-"+ str(self.pk)))
        return recipe_url
        
        
    #---------------------------------------------------------------------------
    def save(self, *args, **kwargs):
        if not self.book:
            self.book = Book.objects.get(pk=1)
        super(Subsection, self).save()
        
