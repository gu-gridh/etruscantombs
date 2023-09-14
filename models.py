# from django.db import models
from django.contrib.gis.db import models
import diana.abstract.models as abstract
from django.utils.translation import gettext_lazy as _
from diana.storages import OriginalFileStorage
from ckeditor.fields import RichTextField
from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD
# Create your models here.

# TODO: add Plan: images of the floor plan
# TODO: add Document: Any document related to a Place 
# TODO: add Observation (simple text)

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
    

# Place
class Place(abstract.AbstractBaseModel):
    
    name = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("name"), help_text=_("Please enter the name of the tomb"))
    geometry = models.GeometryField(verbose_name=_("geometry"), blank=True, null=True)
    parent_id = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, help_text=_("If this tombs is attached to other tombs"))
    tags = models.ManyToManyField(Tag, null=True, blank=True)
    description = RichTextField(null=True, blank=True, help_text=("Descriptive text about the tomb"))
    date = models.ForeignKey(Epoch, on_delete=models.CASCADE, blank=True, null=True, help_text=_("Dating of the tomb"))

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Place")


class Author(abstract.AbstractBaseModel):
    # title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    author_firstname = models.CharField(max_length=256, blank=True, null=True)
    author_lastname = models.CharField(max_length=256, blank=True, null=True)
    # attribution = models.CharField(max_length=256, blank=True, null=True)
    # publication_place = models.CharField(max_length=256, blank=True, null=True)
    # publication_year = models.IntegerField(blank=True, null=True)
    # gupea = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.author_firstname} {self.author_lastname}"
    

class Image(abstract.AbstractTIFFImageModel):

    title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    source_id = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True)
    place   = models.ForeignKey(Place, null=True, blank=True, on_delete=models.CASCADE, related_name="images")
    type = models.CharField(max_length=32, null=True, blank=True, help_text=_("Type of the image can be jpeg, png, etc."))
    image_url = models.CharField(max_length=256, blank=True, null=True)
    description = RichTextField(null=True, blank=True, help_text=("Descriptive text about the images"))

    def __str__(self) -> str:
        return f"{self.title}"
    
    # TODO : add date of image
    

class Layer(abstract.AbstractBaseModel):
    title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    source_id = models.ForeignKey(Author, on_delete=models.CASCADE, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    type = models.CharField(max_length=32, null=True, blank=True)
    format = models.CharField(max_length=32, null=True, blank=True, help_text=_("Type of the image can be jpeg, png, etc."))
    description = RichTextField(null=True, blank=True, verbose_name=_("description"))


class Object3D(abstract.AbstractBaseModel):
    title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    source_id = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True)
    place   = models.ForeignKey(Place, null=True, blank=True, on_delete=models.CASCADE, related_name="object3D")
    type = models.CharField(max_length=32, null=True, blank=True, help_text=_("Type of the object can be 3D-hop or cloudpoint"))
    link_3Dhop = models.CharField(max_length=1024, blank=True, null=True)
    link_pointcloud = models.CharField(max_length=1024, blank=True, null=True)
    description = RichTextField(null=True, blank=True, help_text=("Descriptive text about the 3D object"))

    def __str__(self) -> str:
        return f"{self.title}"
    
    class Meta:
        verbose_name = _("Object 3D")
        verbose_name_plural = _("Objects 3D")

    # QUESTION: are 3D hop and pointcloud mutually exclusive
    # TODO: split this into 3d hop and pointcloud
    # TODO: write in parameters for each
    # TODO: add date of creation
    # TODO: add preview image


class Documentation(abstract.AbstractBaseModel):
    """
    title = 
    place =
    pdf_file_url = 
    date = 
    """