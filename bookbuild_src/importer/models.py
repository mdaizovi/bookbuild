from django.db import models
from django.db.models import Manager
#from ordered_model.models import OrderedModel


#filename is section
# first word in file is also section
# next word is category, then blob of text for category, then items within category.
# Will have a few categories per section.

class BaseModel(models.Model):
    title =  models.CharField(max_length=200)
    order = models.PositiveSmallIntegerField(null = True, blank = True)

    class Meta:
        abstract = True
    
    def __str__(self):
        return "<{}> {}".format(
            self.__class__.__name__, self.title
        )
        

#filename
class Section(BaseModel):
    pass

class Neighborhood(BaseModel):
    pass

#in text file
class Category(BaseModel):
    main_text = models.TextField(null = True, blank = True)
    section = models.ForeignKey(Section, null = True, blank = True, on_delete=models.SET_NULL)


class BlobManager(Manager):
    def get_by_natural_key(self, title):
        return self.get(title=title)
    
class Blob(BaseModel):
#class Blob(OrderedModel):
    
    neighborhood = models.ForeignKey(Neighborhood, null = True, blank = True, on_delete=models.SET_NULL)

    section = models.ForeignKey(Section, null = True, blank = True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null = True, blank = True, on_delete=models.SET_NULL)
    priority = models.PositiveSmallIntegerField(null = True, blank = True)
    #order_with_respect_to = ('book', 'section','category', 'neighborhood')
    category_text = models.TextField(null = True, blank = True)
    main_text = models.TextField(null = True, blank = True)
    footer_text = models.TextField(null = True, blank = True)
    
    soft_delete = models.BooleanField(default=False)

    objects = BlobManager()

    @property
    def char_count(self):
        target = {1:300, 2:300, 3:300, 4:1000, 5:2000}
        if self.main_text and self.priority:
            return f"{len(self.main_text)}/{target[self.priority]}"
        else:
            return ""

    @property
    def has_text(self):
        if self.main_text:
            return True
        else:
            return 

    def natural_key(self):
        return (self.title,)
    
