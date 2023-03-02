import os
from collections import OrderedDict
from docx2python import docx2python
from io import StringIO

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import Section, Neighborhood, Category, Blob

#python manage.py import_source_text --filename 03-ausflug.docx --dryrun

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--filename', type=str,
                help='file name relative to BASE_DIR')               

        parser.add_argument('--verbose',
                action='store_true',
                help='True if you want lots of output')      

        parser.add_argument('--dryrun',
                action='store_true',
                help="True if you don't want to save anything")   

    def handle(self, *args, **options):
        kwargs = {}
        filename = options['filename']
        verbose = options['verbose']
        dryrun = options['dryrun']
     
        if verbose:
            print(f"--Starting to import {filename}")

        filepath = os.path.join(settings.BASE_DIR, "importer", "source", filename)
        #print(f"filepath: {filepath}")

        doc_result = docx2python(f"{filepath}")
        body = [x.strip() for x in doc_result.body[0][0][0] if len(x)>1]
        #print(body)
        section, _  = Section.objects.get_or_create(title=body[0])
        print(f"{section}")
        if not dryrun:
            section.save()


        titles = {body.index(x): x for x in body if "[" in x and "]" in x}
        #print(titles)
        sorted = list(titles.keys())
        sorted.sort()
        sorted_titles = OrderedDict()
        for t in sorted:
            sorted_titles[t] = titles.get(t)
        #print(sorted)    
        #print(sorted_titles)

        i = 0
        #for element in body[1:20]:
        for element in body[1:]:
            i+=1
            if i in sorted:
                #print(f"i: {i}")
                if i == sorted[-1]:
                    next_index = None
                else:
                    this_sorted_index = sorted.index(i)
                    next_index = sorted[this_sorted_index+1]
                #print(f"next: {next_index}")
                if next_index:
                    this_section = body[i:next_index]
                else:
                    this_section = body[i:]
                #print(f"this_section: {this_section}")

                #TODO how to get nxt category?
                # if i == sorted[0]:
                #     previous_index = None
                # else:
                #     this_sorted_index = sorted.index(i)
                #     previous_index = sorted[this_sorted_index-1]





                possible_category_title = body[i-2]
                possible_category_body = body[i-1]
                if "href" not in possible_category_body and "href" not in possible_category_title:
                    category, _  = Category.objects.get_or_create(title=possible_category_title, main_text=possible_category_body)
                    if not dryrun:
                        category.save()          
                    print(f"\n---------\n{category}\n---------")
                    print(f"{category.main_text}")
                
                title_list = sorted_titles.get(i).split('[')
                blob_title = title_list[0]
                neighborhood_title = title_list[1][:-1]

                neighborhood, _ = Neighborhood.objects.get_or_create(title=neighborhood_title)
                if not dryrun:
                    neighborhood.save()  
                print(f"\n{neighborhood}\n")
                
                # footer is the first part of this_section thst contains href, until end.
                hi = -1
                for e in this_section:
                    hi+=1
                    if "href" in e:
                        break
                main_text_list=this_section[1:hi]
                footer_text_list=this_section[hi:]

                main_text = "\n".join(main_text_list)
                footer_text = "\n".join(footer_text_list)

                blob, _  = Blob.objects.get_or_create(category=category, neighborhood=neighborhood, section=section, 
                        title = blob_title,
                        main_text=main_text,
                        footer_text=footer_text)
                if not dryrun:
                    blob.save()           
                
                print(f"\n{blob}\n")
                for v in ["category", "neighborhood", "section", "title", "main_text", "footer_text"]:
                    attr = getattr(blob, v)
                    print(f"{v}: {attr}")
                print("\n\n")
                


    
        if verbose:
            print(f"--finished importing {filename}")