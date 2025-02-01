from ..models import Book, Subsection
from ..model_enum import ChapterTypeChoices


class BookQueries:
    @staticmethod
    def get_book(pk=1):
        return Book.objects.get(pk=pk)

    @staticmethod
    def get_all_images(book):
        return Book.objects.get_images(book)

    @staticmethod
    def get_all_files(book):
        return book.files.all()

    @staticmethod
    def get_all_chapters(book, order_by="playOrder"):
        base_query = book.chapter_set.all()
        if order_by is not None:
            base_query = base_query.order_by(order_by)
        return base_query

    @staticmethod
    def get_all_chapter_sections(chapter):
        return chapter.section_set.all()

    @staticmethod
    def get_content_chapters(book, order_by="playOrder"):
        """Returns list of all chapters that inclide content
        (ie exludes title page, copyright, contents)
        """
        exclude = [
            ChapterTypeChoices.CHAPTER_TP,
            ChapterTypeChoices.CHAPTER_CR,
            ChapterTypeChoices.CHAPTER_C,
        ]
        base_query = book.chapter_set.all().exclude(chapter_type__in=exclude)
        if order_by is not None:
            base_query = base_query.order_by(order_by)
        return base_query

    @staticmethod
    def get_chapters_except_contents(book, order_by="playOrder"):
        base_query = book.chapter_set.all().exclude(
            chapter_type=ChapterTypeChoices.CHAPTER_C
        )
        if order_by is not None:
            base_query = base_query.order_by(order_by)
        return base_query

    @staticmethod
    def get_contents_chapter(book):
        return book.chapter_set.filter(
            chapter_type=ChapterTypeChoices.CHAPTER_C
        ).first()

    @staticmethod
    def get_section_list_subsections(section):
        """Returns list of all subsections in a chapter section
        EXCEPT for prio 5 items
        """
        return [
            x
            for x in section.subsection_set.filter(priority__lte=4).order_by(
                "-priority", "order"
            )
        ]

    @staticmethod
    def get_chapter_top5(chapter):
        def nonesorter(a):
            if not a.order:
                return 0
            return a.order

        top5 = []
        for section in chapter.section_set.all():
            top5 += [
                x
                for x in section.subsection_set.filter(priority__gte=5).order_by(
                    "order"
                )
            ]
        top5.sort(key=lambda x: nonesorter(x), reverse=True)
        return top5

    @staticmethod
    def chapter_has_sections(chapter):
        return chapter.section_set.all().count() > 0

    @staticmethod
    def get_subsection_for_chapters(chapters):
        return Subsection.objects.filter(section__chapter__in=chapters).order_by(
            "title"
        )
