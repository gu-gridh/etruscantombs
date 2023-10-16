import os
import PIL
import shutil
from .models import Place

local_folder = "../../../Utils_EtruscanTombs/SG_tombs_data_dump/Test_data_dump"

def fetch_tomb_id_from_name(filename):
    tomb_name, _ = filename.split("_")
    tomb = Place.objects.get(name=tomb_name)
    
    return tomb.id

def upload_image(filename):
    pass

    
def batch_upload(folder):
    for image in folder:
        pass