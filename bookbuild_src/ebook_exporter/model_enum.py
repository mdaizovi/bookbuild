class FileTypeChoices():
    FONT = "fonts"
    IMG = "images"
    CSS = "css"
    CHOICES = [
        (FONT, FONT),
        (IMG, IMG),
        (CSS, CSS),
    ]

class BookTypeChoices():
    TRAVELGUIDE = "TG"
    NONFICTION = "NF"
    CHOICES = [
        (NONFICTION, "nonfiction"),
        (TRAVELGUIDE, "travelguide"),
    ]

class LanguageTypeChoices():
    ENGLISH = "EN"
    GERMAN = "DE"
    CHOICES = [
        (ENGLISH, "English"),
        (GERMAN, "German"),
    ]

class MediaTypeChoices():
    MEDIA_JPEG = "jpg"
    MEDIA_HTML = "html"
    MEDIA_DTBNCX = "dtbncx"
    MEDIA_CSS = "css"
    MEDIA_VND = "vnd"

    CHOICES = [
        (MEDIA_JPEG, "image/jpeg"),
        (MEDIA_HTML, "application/xhtml+xml"),
        (MEDIA_DTBNCX, "application/x-dtbncx+xml"),
        (MEDIA_CSS, "text/css"),
        (MEDIA_VND, "application/vnd.ms-opentype"),
    ]

 
class ChapterTypeChoices():
    CHAPTER_TP = "TP"
    CHAPTER_CR = "CR"
    CHAPTER_C = "C"
    CHAPTER_CH = "CH"
    
    CHOICES = [
        (CHAPTER_TP, "Title Page"),
        (CHAPTER_CR, "Copyright"),
        (CHAPTER_C, "Contents"),
        (CHAPTER_CH, "Chapter"),
    ]
