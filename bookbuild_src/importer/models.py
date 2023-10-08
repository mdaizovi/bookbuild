from django.db import models

class BaseModel(models.Model):
    title = models.CharField(max_length=200)
    order = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "<{}> {}".format(self.__class__.__name__, self.title)

#### Neighborhood is basically chapter
class Neighborhood(BaseModel):
    pass

class Section(BaseModel):
    pass

class Category(BaseModel):
    main_text = models.TextField(null=True, blank=True)
    section = models.ForeignKey(
        Section, null=True, blank=True, on_delete=models.SET_NULL
    )


class Blob(BaseModel):
    neighborhood = models.ForeignKey(
        Neighborhood, null=True, blank=True, on_delete=models.SET_NULL
    )

    section = models.ForeignKey(
        Section, null=True, blank=True, on_delete=models.SET_NULL
    )
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL
    )
    priority = models.PositiveSmallIntegerField(null=True, blank=True)
    # order_with_respect_to = ('book', 'section','category', 'neighborhood')
    category_text = models.CharField(null=True, blank=True, max_length=200)
    main_text = models.TextField(null=True, blank=True)
    footer_text = models.TextField(null=True, blank=True)

    soft_delete = models.BooleanField(default=False)

