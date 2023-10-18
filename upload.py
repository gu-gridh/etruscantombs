import os
import sys
import PIL
import shutil
from .models import *

local_folder = sys.args[1]
if len(sys.args) == 1:
    local_folder = "../../../Utils_EtruscanTombs/SG_tombs_data_dump/Test_data_dump/"

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
    tomb_name, author, creation_date, image_type, identifier = filename.split("_")
    
    author_firstname, author_lastname = author.split("-")
    
    tomb = get_or_none(Place, **{"name": tomb_name})
    author = get_or_none(Author, **{"firstname": author_firstname, "lastname": author_lastname})
    type_of_image = get_or_none(TypeOfImage, **{"text": image_type})
    
    image = Image(
        author = author,
        tomb = tomb,
        type_of_image = type_of_image,
        date = creation_date
    )
    
    image.save()

    
def batch_upload(folder):
    
    for imagepath in os.listdir(folder):
        upload_image(imagepath)
        
        
if __name__ == '__main__':
    batch_upload(local_folder)