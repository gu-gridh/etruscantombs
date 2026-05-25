import os
import sys

# Running this file directly from the app folder puts that folder first on sys.path,
# which shadows the stdlib signal module with local signal.py during Django imports.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if CURRENT_DIR in sys.path:
    sys.path.remove(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "diana.settings")

import django

django.setup()

from apps.etruscantombs.models import Author, Image, Place, TypeOfImage
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.db import models, transaction

CONNECT_TIMEOUT = float(os.getenv("IIIF_CONNECT_TIMEOUT", "5"))
READ_TIMEOUT = float(os.getenv("IIIF_READ_TIMEOUT", "20"))
MAX_RETRIES = int(os.getenv("IIIF_MAX_RETRIES", "3"))


def _build_http_session():
    retry = Retry(
        total=MAX_RETRIES,
        connect=MAX_RETRIES,
        read=MAX_RETRIES,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


HTTP_SESSION = _build_http_session()

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
        tomb_name, author, creation_date, image_type, identifier = filename.split("_")
    except:
        try:
            tomb_name, author, creation_date, image_type, identifier, hdr = filename.split("_")
        except:
            return
    
    author_firstname, author_lastname = author.split("-")
    tomb_name = str(int(tomb_name))
    
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
            file = os.path.join("etruscantombs/original", filename),
            date = creation_date
        ) # title = f"Documentation {identifier}",
    
        image.save()
        image.type_of_image.add(image_type)
    else:
        print(f"Changing file {filename}")
        fetch_existing_image.update(tomb=tomb)

    
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
        

def update_image_metadata(sender, instance, **kwargs):
    """Fetch and update image dimensions from IIIF info.json if not set."""
    if instance is None:
        return False
    
    if (instance.width is None or instance.height is None) and instance.iiif_file:
        base_url = "https://img.dh.gu.se/diana/static/"
        iiif_file_url = getattr(instance.iiif_file, 'url', None)
        if not iiif_file_url:
            return False
        if not iiif_file_url.startswith("http"):
            iiif_file_url = base_url + iiif_file_url.lstrip("/")
        info_url = f"{iiif_file_url}/info.json"
        try:
            response = HTTP_SESSION.get(info_url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
            if response.status_code == 200:
                info = response.json()
                width = info.get("width")
                height = info.get("height")
                # Only update if values are present
                if width and height:
                    # Schedule this to run after the current transaction commits
                    # This ensures M2M fields are saved first
                    def update_dimensions():
                        Image.objects.filter(pk=instance.pk).update(width=width, height=height)
                    
                    transaction.on_commit(update_dimensions)
                    return True
            return False
        except requests.exceptions.Timeout as e:
            print(f"Timeout fetching IIIF info for image {instance.id}: {e}")
            return False
        except Exception as e:
            # Optionally log the error
            print(f"Could not fetch IIIF info for image {instance.id}: {e}")
            return False

    return False


def backfill_image_metadata():
    images = Image.objects.filter(models.Q(width__isnull=True) | models.Q(height__isnull=True))
    total = images.count()
    print(f"Checking {total} images for missing metadata")

    updated = 0
    failed = 0

    for image in images.iterator():
        if update_image_metadata(None, image):
            updated += 1
        else:
            failed += 1

    print(f"Updated: {updated} | Not updated: {failed}")
    print("Metadata backfill run completed")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        backfill_image_metadata()
    elif sys.argv[1] == "upload":
        if len(sys.argv) < 3:
            raise SystemExit("Usage: python upload.py upload <folder>")
        batch_upload(sys.argv[2])
    else:
        raise SystemExit("Usage: python upload.py [upload <folder>]")