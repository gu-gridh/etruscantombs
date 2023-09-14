# from django.db import models
from django.contrib.gis.db import models
import diana.abstract.models as abstract
from django.utils.translation import gettext_lazy as _
from diana.storages import OriginalFileStorage
from diana.abstract.models import get_original_path
from ckeditor.fields import RichTextField
from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD
from datetime import date
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
    

class Author(abstract.AbstractBaseModel):
    firstname = models.CharField(max_length=256, blank=True, null=True)
    lastname = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname}"
    

# Place
class Place(abstract.AbstractBaseModel):
    
    name = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("name"), help_text=_("Please enter the name of the tomb"))
    geometry = models.GeometryField(verbose_name=_("geometry"), blank=True, null=True)
    parent_id = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, help_text=_("If this tombs is attached to other tombs"))
    type = models.ForeignKey(TypeOfTomb, on_delete=models.CASCADE, null=True, blank=True, help_text=_("Type of the tomb"))
    tags = models.ManyToManyField(Tag, blank=True, help_text=_("Tags attached to the tomb"))
    description = RichTextField(null=True, blank=True, help_text=("Descriptive text about the tomb"))
    epoch = models.ForeignKey(Epoch, on_delete=models.CASCADE, blank=True, null=True, help_text=_("Dating of the tomb"))
    default_image = models.ForeignKey("Image", on_delete=models.CASCADE, null=True, blank=True, help_text=_("Default image showing on preview"))
    default_3DHop = models.ForeignKey("Object3DHop", on_delete=models.CASCADE, null=True, blank=True, help_text=_("Default image showing on preview"))
    default_pointcloud = models.ForeignKey("ObjectPointCloud", on_delete=models.CASCADE, null=True, blank=True, help_text=_("Default image showing on preview"))

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Place")


class Image(abstract.AbstractTIFFImageModel):

    title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True)
    tomb   = models.ForeignKey(Place, null=True, blank=True, on_delete=models.CASCADE, related_name="images")
    type = models.CharField(max_length=32, null=True, blank=True, help_text=_("Type of the image can be 'floor plan' or 'image'"))
    format = models.CharField(max_length=32, null=True, blank=True, help_text=_("Type of the image can be jpg, png, etc"))
    image_url = models.CharField(max_length=256, blank=True, null=True)
    description = RichTextField(null=True, blank=True, help_text=("Descriptive text about the images"))
    date = models.DateField(default=date.today, help_text=_("Date in which the image was taken"))

    def __str__(self) -> str:
        return f"{self.title}"
    

class Layer(abstract.AbstractBaseModel):
    title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    author = models.ForeignKey(Author, on_delete=models.CASCADE, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    type = models.CharField(max_length=32, null=True, blank=True)
    format = models.CharField(max_length=32, null=True, blank=True, help_text=_("Type of the image can be jpeg, png, etc."))
    description = RichTextField(null=True, blank=True, verbose_name=_("description"))


class Object3DHop(abstract.AbstractBaseModel):
    title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    author = models.ManyToManyField(Author, blank=True)
    tomb   = models.ForeignKey(Place, null=True, blank=True, on_delete=models.CASCADE, related_name="object_3Dhop")
    url = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("3D-Hop URL"))
    description = RichTextField(null=True, blank=True, help_text=("Descriptive text about the 3D object"))
    date = models.DateField(default=date.today, help_text=_("Date in which the 3D object was created"))
    
    trackball_start = ArrayField(models.FloatField(), size=6, default=list)
    start_angle = ArrayField(models.FloatField(), size=2, default=list, verbose_name=_("Start angle (phi, theta)"))
    start_distance = models.FloatField(null=True, blank=True, verbose_name=_("initial mesh distance"))
    start_pan = ArrayField(models.FloatField(), size=3, default=get_list_zeros)
    min_max_phi = ArrayField(models.FloatField(), size=3, default=get_min_max_default, verbose_name=_("maximal vertical camera angles"))
    min_max_theta = ArrayField(models.FloatField(), size=3, default=get_min_max_default, verbose_name=_("maximal horizontal camera angles"))

    preview_image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self) -> str:
        return f"{self.title}"
    
    class Meta:
        verbose_name = _("Object 3D-hop")
        verbose_name_plural = _("Objects 3D-hop")

    # TODO: add default naming conventions to forms (auto-generated links)


class ObjectPointCloud(abstract.AbstractBaseModel):
    title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    author = models.ManyToManyField(Author, blank=True)
    tomb   = models.ForeignKey(Place, null=True, blank=True, on_delete=models.CASCADE, related_name="object_pointcloud")
    url = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("Pointcloud URL"))
    description = RichTextField(null=True, blank=True, help_text=("Descriptive text about the 3D object"))
    date = models.DateField(default=date.today, help_text=_("Date in which the 3D object was created"))

    camera_position = ArrayField(models.FloatField(), size=3, default=list)
    look_at = ArrayField(models.FloatField(), size=3, default=list)

    def __str__(self) -> str:
        return f"{self.title}"
    
    class Meta:
        verbose_name = _("Object Pointcloud")
        verbose_name_plural = _("Objects Pointcloud")


class Document(abstract.AbstractBaseModel):
    title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True)
    place = models.ForeignKey(Place, null=True, blank=True, on_delete=models.CASCADE, related_name="documentation")
    upload = models.FileField(storage=OriginalFileStorage, upload_to=get_original_path, verbose_name=_("general.file"), default=None)
    # document_url = models.CharField(max_length=256, blank=True, null=True)
    description = RichTextField(null=True, blank=True, help_text=("Descriptive text about the document"))
    date = models.DateField(default=date.today, help_text=_("Date in which the document was created"))

    def __str__(self) -> str:
        return f"{self.title}"
    
    class Meta:
        verbose_name = _("Document")


class Observation(abstract.AbstractBaseModel):
    title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True)
    place = models.ForeignKey(Place, null=True, blank=True, on_delete=models.CASCADE, related_name="observation")
    observation = RichTextField(null=True, blank=True, help_text=("Write observation here"))
    date = models.DateField(default=date.today, help_text=_("Date in which the document was created"))
    
    # QUESTION does this model needs a "related image" field? E.g. to update hand written notes, it could be either an Image or a Document