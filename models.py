# from django.db import models
from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 
import diana.abstract.models as abstract
from django.utils.translation import gettext_lazy as _
from diana.storages import OriginalFileStorage, IIIFFileStorage
from diana.abstract.models import get_original_path, get_iiif_path
from ckeditor.fields import RichTextField
from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD
from datetime import date
from .validators import validate_file_extension, validate_image_extension

# Create your models here.

from django.contrib.postgres.fields import ArrayField
def get_list_zeros():
    return [0.0, 0.0, 0.0]
def get_min_max_default():
    return [-180, 180]

class Tag(abstract.AbstractTagModel):
    
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    

class Epoch(abstract.AbstractTagModel):
    
    class Meta:
        verbose_name = _("Epoch")
        verbose_name_plural = _("Epochs")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    

class TypeOfTomb(abstract.AbstractTagModel):

    class Meta:
        verbose_name = _("Type of tomb")
        verbose_name_plural = _("Types of tombs")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    

class TypeOfImage(abstract.AbstractTagModel):

    class Meta:
        verbose_name = _("Type of image")
        verbose_name_plural = _("Types of image")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    

class TypeOfDocument(abstract.AbstractTagModel):

    class Meta:
        verbose_name = _("Type of document")
        verbose_name_plural = _("Types of document")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    

class TypeOfObservation(abstract.AbstractTagModel):

    class Meta:
        verbose_name = _("Type of observation")
        verbose_name_plural = _("Types of observation")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)


class Site(abstract.AbstractTagModel):
    
    class Meta:
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    

class Necropolis(abstract.AbstractTagModel):
    
    geometry = models.GeometryField(verbose_name=_("geometry"), blank=True, null=True, default=None)
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Archaeological site in which the Necropolis is found"))

    class Meta:
        verbose_name = _("Necropolis")
        verbose_name_plural = _("Necropolis")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    

class Technique3D(abstract.AbstractTagModel):

    class Meta:
        verbose_name = _("3D technique")
        verbose_name_plural = _("3D techniques")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    

class Author(abstract.AbstractBaseModel):
    firstname = models.CharField(max_length=256, blank=True, null=True)
    lastname = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname}"
    
    
class Dataset(abstract.AbstractBaseModel):
    name = models.CharField(max_length=1024, blank=True, null=True, help_text=("Full name of the dataset"))
    short_name = models.CharField(max_length=64, blank=True, null=True, help_text=("Name of the dataset to use for filtering"))
    description = RichTextField(null=True, blank=True, help_text=("Descriptive text about the dataset"))
    contributors = models.ManyToManyField(Author, blank=True, default=None, help_text=_("People who contributed to the dataset"))
    # attached_document = models.ForeignKey("Document", on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Document or publication relating the dataset"))

    def __str__(self) -> str:
        return self.name


# Tomb model
class Place(abstract.AbstractBaseModel):
    
    name = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("name"), help_text=_("Please enter the name of the tomb"))
    subtitle = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("subtitle"), default = None)
    clone_tombs = models.ManyToManyField("self", blank=True, help_text=_("Add here instances of the same tomb from other datasets."), verbose_name=_("Same as"))
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True, default=1, help_text=_("Datasets in which this tomb was reported."), related_name=("tomb"))
    geometry = models.GeometryField(verbose_name=_("geometry"), blank=True, null=True)
    necropolis = models.ForeignKey(Necropolis, null=True, blank=True, on_delete=models.SET_NULL)
    type = models.ForeignKey(TypeOfTomb, on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Type of the tomb"))
    number_of_chambers = models.FloatField(null=True, blank=True, verbose_name=_("number of chambers"))
    tags = models.ManyToManyField(Tag, blank=True, help_text=_("Tags attached to the tomb"))
    description = RichTextField(null=True, blank=True, help_text=("Descriptive text about the tomb"))
    epoch = models.ForeignKey(Epoch, on_delete=models.SET_NULL, blank=True, null=True, help_text=_("Dating of the tomb"))
    min_year = models.IntegerField(null=True, blank=True, default=625, help_text=_("Oldest assigned year (BC)"))
    max_year = models.IntegerField(null=True, blank=True, default=400, help_text=_("Oldest assigned year (BC)"))
    default_image = models.ForeignKey("Image", on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Default image showing on preview"))
    
    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Tomb")
        verbose_name_plural = _("Tombs")
        
    def list_all_pk(self):
        all_pk = []
        for obj in Place.objects.all().order_by('pk'):
            all_pk.append(obj.pk)
        return all_pk
        
    def next(self):
        all_pk = self.list_all_pk()
        current_index = all_pk.index(self.pk)
        try: 
            return Place.objects.get(pk=all_pk[current_index+1])
        except: 
            return None
        
    def previous(self):
        all_pk = self.list_all_pk()
        current_index = all_pk.index(self.pk)
        try:
            return Place.objects.get(pk=all_pk[current_index-1])
        except:
            return None


class Image(abstract.AbstractTIFFImageModel):

    title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True)
    tomb   = models.ForeignKey(Place, null=True, blank=True, on_delete=models.CASCADE, related_name="images")
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True, default=1, help_text=_("Datasets in which this tomb was reported."))
    type_of_image = models.ManyToManyField(TypeOfImage, blank=True)
    description = RichTextField(null=True, blank=True, help_text=("Descriptive text about the images"))
    date = models.DateField(default=date.today, help_text=_("Date in which the image was taken"))

    # Image metadata
    width = models.IntegerField(null=True, blank=True, verbose_name=_("width (px)"))
    height = models.IntegerField(null=True, blank=True, verbose_name=_("height (px)"))

    def __str__(self) -> str:
        return f"{self.title}"
    
    
    def list_all_pk(self):
        all_pk = []
        for obj in Image.objects.all().order_by('pk'):
            all_pk.append(obj.pk)
        return all_pk
        
    def next(self):
        all_pk = self.list_all_pk()
        current_index = all_pk.index(self.pk)
        try: 
            return Image.objects.get(pk=all_pk[current_index+1])
        except: 
            return None
        
    def previous(self):
        all_pk = self.list_all_pk()
        current_index = all_pk.index(self.pk)
        try:
            return Image.objects.get(pk=all_pk[current_index-1])
        except:
            return None

class Formats3D(models.IntegerChoices):
    GLB = 1, "GLB"
    USDZ = 2, "USDZ"

class Object3DHop(abstract.AbstractBaseModel):
    title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    subtitle = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("subtitle"))
    author = models.ManyToManyField(Author, blank=True)
    tomb   = models.ManyToManyField(Place, blank=True, related_name="object_3Dhop")
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True, default=1, help_text=_("Datasets in which this tomb was reported."))
    url_public = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("URL for API call"))
    url_download = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("URL for download"))
    url_source = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("URL for source files"))
    triangles_optimized = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("Triangles (optimized)"), help_text=_("number of triangles of the optimized mesh, e.g.: 250 millions"))
    triangles_full_resolution = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("Triangles (full resolution)"), help_text=_("number of triangles of the full resolution mesh, e.g.: 1.3 billions"))
    description = RichTextField(null=True, blank=True, help_text=("Descriptive text about the 3D object"))
    date = models.DateField(default=date.today, help_text=_("Date in which the 3D object was created"))
    technique = models.ForeignKey(Technique3D, null=True, blank=True, on_delete=models.SET_NULL, help_text=_("Technique used to generate the 3D model"))
    scaled = models.BooleanField(help_text=_("If the model is scaled, please check the box"), default=False)
    
    trackball_start = ArrayField(models.FloatField(), size=6, default=list)
    start_angle = ArrayField(models.FloatField(), size=2, default=list, verbose_name=_("Start angle (phi, theta)"), help_text=_("Format: 2 comma-separated float numbers, e.g.: 0.0, 1.1"))
    start_distance = models.FloatField(null=True, blank=True, verbose_name=_("initial mesh distance"))
    start_pan = ArrayField(models.FloatField(), size=3, default=get_list_zeros, help_text=_("Format: 3 comma-separated float numbers, e.g.: 0.0, 1.1, 2.2"))
    min_max_phi = ArrayField(models.FloatField(), size=2, default=get_min_max_default, verbose_name=_("maximal vertical camera angles"), help_text=_("Format: 2 comma-separated float numbers, e.g.: 0.0, 1.1"))
    min_max_theta = ArrayField(models.FloatField(), size=2, default=get_min_max_default, verbose_name=_("maximal horizontal camera angles"), help_text=_("Format: 2 comma-separated float numbers, e.g.: 0.0, 1.1"))

    preview_image = models.ImageField(max_length=256, storage=OriginalFileStorage, upload_to='etruscantombs/previewimages/', blank=True, null=True, verbose_name=_("Preview image"))
# models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self) -> str:
        return f"{self.title}"
    
    class Meta:
        verbose_name = _("Object Detailed Mesh")
        verbose_name_plural = _("Objects Detailed Mesh")

    # TODO: add default naming conventions to forms (auto-generated links)


class ObjectPointCloud(abstract.AbstractBaseModel):
    title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    subtitle = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("subtitle"))
    author = models.ManyToManyField(Author, blank=True)
    tomb   = models.ManyToManyField(Place, blank=True, related_name="object_pointcloud")
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True, default=1, help_text=_("Datasets in which this tomb was reported."))
    url_public = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("URL for API call"))
    url_download = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("URL for download"))
    url_source = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("URL for source files"))
    points_optimized = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("Points (optimized)"), help_text=_("number of points of the optimized models, e.g.: 250 millions"))
    points_full_resolution = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("Points (full resolution)"),  help_text=_("number of points of the full resolution model, e.g.: 1.3 billions"))
    description = RichTextField(null=True, blank=True, help_text=("Descriptive text about the 3D object"))
    date = models.DateField(default=date.today, help_text=_("Date in which the 3D object was created"))
    technique = models.ForeignKey(Technique3D, null=True, blank=True, on_delete=models.SET_NULL, help_text=_("Technique used to generate the 3D model"))
    scaled = models.BooleanField(help_text=_("If the model is scaled, please check the box"), default=False)

    camera_position = ArrayField(models.FloatField(), size=3, default=get_list_zeros, help_text=_("Format: 3 comma-separated float numbers, e.g.: 0.0, 1.1, 2.2"))
    look_at = ArrayField(models.FloatField(), size=3, default=get_list_zeros, help_text=_("Format: 3 comma-separated float numbers, e.g.: 0.0, 1.1, 2.2"))

    preview_image = models.ImageField(max_length=256, storage=OriginalFileStorage, upload_to='etruscantombs/previewimages/', blank=True, null=True, verbose_name=_("Preview image"))# models.ImageField(max_length=256, storage=IIIFFileStorage, upload_to=get_iiif_path, blank=True, null=True, verbose_name=_("Preview image"))

    def __str__(self) -> str:
        return f"{self.title}"
    
    class Meta:
        verbose_name = _("Object Pointcloud")
        verbose_name_plural = _("Objects Pointcloud")


class Object3js(abstract.AbstractBaseModel):
    title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    subtitle = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("subtitle"))
    author = models.ManyToManyField(Author, blank=True)
    tomb   = models.ManyToManyField(Place, blank=True, related_name="object_3js")
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True, default=1, help_text=_("Datasets in which this tomb was reported."))
    url_public = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("URL for API call"))
    url_download = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("URL for download"))
    url_source = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("URL for source files"))
    format_3d = models.IntegerField(choices=Formats3D.choices, default=1, verbose_name=_("3D Format"))
    
    description = RichTextField(null=True, blank=True, help_text=("Descriptive text about the 3D object"))
    date = models.DateField(default=date.today, help_text=_("Date in which the 3D object was created"))
    technique = models.ForeignKey(Technique3D, null=True, blank=True, on_delete=models.SET_NULL, help_text=_("Technique used to generate the 3D model"))
    scaled = models.BooleanField(help_text=_("If the model is scaled, please check the box"), default=False)
    polygons = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("Polygons"), help_text=_("number of triangles of the optimized mesh, e.g.: 5 millions"))
    camera_position = ArrayField(models.FloatField(), size=3, default=get_list_zeros, help_text=_("Format: 3 comma-separated float numbers, e.g.: 0.0, 1.1, 2.2"))
    look_at = ArrayField(models.FloatField(), size=3, default=get_list_zeros, help_text=_("Format: 3 comma-separated float numbers, e.g.: 0.0, 1.1, 2.2"))
    movement_speed = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    preview_image = models.ImageField(max_length=256, storage=OriginalFileStorage, upload_to='etruscantombs/previewimages/', blank=True, null=True, verbose_name=_("Preview image"))# models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.title}"
    
    class Meta:
        verbose_name = _("Object Textured")
        verbose_name_plural = _("Objects Textured Mesh")


class Document(abstract.AbstractBaseModel):
    title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True)
    place = models.ManyToManyField(Place, blank=True, related_name="documentation")
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True, default=1, help_text=_("Datasets in which this tomb was reported."))
    upload = models.FileField(null=True, blank=True, storage=OriginalFileStorage, upload_to=get_original_path, verbose_name=_("file"), validators=[validate_file_extension])
    type = models.ManyToManyField(TypeOfDocument, blank=True, verbose_name=_("Type of document: Report, Thesis, etc"))
    size = models.FloatField(null=True, blank=True, help_text=_("Document size in mb"), default=None)
    description = RichTextField(null=True, blank=True, help_text=("Descriptive text about the document"))
    date = models.DateField(default=date.today, help_text=_("Date in which the document was created"))


    def __str__(self) -> str:
        return f"{self.title}"
    
    class Meta:
        verbose_name = _("Document")


class Observation(abstract.AbstractBaseModel):
    title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True)
    place = models.ForeignKey(Place, null=True, blank=True, on_delete=models.CASCADE, related_name="observation")
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True, default=1, help_text=_("Datasets in which this tomb was reported."))
    observation = RichTextField(null=True, blank=True, help_text=("Write observation here"))
    type = models.ManyToManyField(TypeOfObservation, blank=True, verbose_name=_("Type of the observation: Survey, Damage report, etc"))
    date = models.DateField(default=date.today, help_text=_("Date in which the document was created"))
    
    # QUESTION does this model needs a "related image" field? E.g. to update hand written notes, it could be either an Image or a Document