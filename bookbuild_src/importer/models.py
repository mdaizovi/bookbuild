from django.db import models
from django.db.models import Manager
#from ordered_model.models import OrderedModel


#filename is section
# first word in file is also section
# next word is ctegory, then blob of text for category, then items within category.
# Will have a few categories per section.

class BaseModel(models.Model):
    title =  models.CharField(max_length=200)

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
   
    main_text = models.TextField(null = True, blank = True)
    footer_text = models.TextField(null = True, blank = True)
    
    soft_delete = models.BooleanField(default=False)

    objects = BlobManager()

    @property
    def has_text(self):
        if self.main_text:
            return True
        else:
            return 

    def natural_key(self):
        return (self.title,)
    
