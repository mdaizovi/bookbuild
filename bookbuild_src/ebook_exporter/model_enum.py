class FileTypeChoices:
    FONT = "fonts"
    IMG = "images"
    CSS = "css"
    CHOICES = [
        (FONT, FONT),
        (IMG, IMG),
        (CSS, CSS),
    ]


class BookTypeChoices:
    TRAVELGUIDE = "TG"
    NONFICTION = "NF"
    CHOICES = [
        (NONFICTION, "nonfiction"),
        (TRAVELGUIDE, "travelguide"),
    ]


class LanguageTypeChoices:
    ENGLISH = "EN"
    GERMAN = "DE"
    CHOICES = [
        (ENGLISH, "English"),
        (GERMAN, "German"),
    ]


class MediaTypeChoices:
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


class ChapterTypeChoices:
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


class FooterDetailChoices:
    BTS = "BTS"
    BTS_GOLD = "BTSG"
    ARL = "ARL"
    BRT = "BRT"
    MRT = "MRT"
    MRT_PINK = "MRTPK"
    MRT_PURPLE = "MRTPPL"
    MRT_YELLOW = "MRTYLW"
    SRT = "SRT"
    SRT_LIGHT_RED = "SRTLR"
    SRT_DARK_RED = "SRTDR"
    KANAL = "K"
    FLUSS = "F"
    RAILWAY = "RAIL"
    WEB = "W"
    GOOGLE_MAPS = "GM"
    CHOICES = (
        (BTS, "BTS"),
        (BTS_GOLD, "BTS Gold"),
        (ARL, "ARL"),
        (BRT, "BRT"),
        (MRT, "MRT"),
        (MRT_PINK, "MRT Pink"),
        (MRT_PURPLE, "MRT Purple"),
        (MRT_YELLOW, "MRT Yellow"),
        (SRT, "SRT"),
        (SRT_LIGHT_RED, "SRT Light Red"),
        (SRT_DARK_RED, "SRT Dark Red"),
        (KANAL, "Kanalboot"),
        (FLUSS, "Flussboot"),
        (WEB, "Website"),
        (GOOGLE_MAPS, "Google Maps"),
    )
