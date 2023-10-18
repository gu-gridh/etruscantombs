from django.core.management.base import BaseCommand
from apps.etruscantombs.upload import batch_upload
from diana.settings_local import MEDIA_ROOT

class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument("-b", "--root", type=str)
        
    def handle(self, **options):
        
        folder_path = options["root"]
        
        if folder_path is None:
            folder_path = MEDIA_ROOT
        
        batch_upload(folder_path)