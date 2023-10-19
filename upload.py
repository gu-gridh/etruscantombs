import os
from django.core.files import File
from .models import *

# local_folder = sys.args[1]
# if len(sys.args) == 1:
#     local_folder = "~/Documents/06_Development/03_GRIDH/Utils_EtruscanTombs/SG_tombs_data_dump/Test_data_dump/"

def get_or_none(classmodel: models.Model, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None
    except ValueError:
        return None
    except classmodel.MultipleObjectsReturned:
        return None


def fetch_tomb_id_from_name(filename):
    tomb_name, _ = filename.split("_")
    tomb = Place.objects.get(name=tomb_name)
    
    return tomb.id

def upload_image(filename):
    
    try:
        # if format isn't recognized, return nothing
        tomb_name, author, creation_date, image_type, _ = filename.split("_")
    except:
        return
    
    author_firstname, author_lastname = author.split("-")
    
    tomb = get_or_none(Place, **{"name": tomb_name})
    author = get_or_none(Author, **{"firstname": author_firstname, "lastname": author_lastname})
    image_type = get_or_none(TypeOfImage, **{"text": image_type})
    
    print(f"Managing file {filename}")
    fetch_existing_image = Image.objects.filter(file__icontains=filename)
    
    if len(fetch_existing_image) == 0:
        print(f"Uploading file {filename}")
        image = Image(
            author = author,
            tomb = tomb,
            file = filename,
            date = creation_date
        ) # title = f"Documentation {identifier}",
    
        image.save()
        image.type_of_image.add(image_type)

    
def batch_upload(folder):
    
    files = filter(lambda f: os.path.isfile(os.path.join(folder, f)), os.listdir(folder))
    
    for imagepath in sorted(files):
        
        file_name_proper, extension = imagepath.split(".")
        
        try:
            tomb_name = int(file_name_proper[:3])
            is_tomb_file = isinstance(tomb_name, int)
        except:
            is_tomb_file = False
            
        if extension == "jpg" and is_tomb_file:
            upload_image(imagepath)
        