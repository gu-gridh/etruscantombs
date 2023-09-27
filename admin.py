from django.contrib.gis.db import models
from .models import *
from .forms import *
from django.utils.html import format_html
from django.contrib.gis import admin
from django.utils.translation import gettext_lazy as _
from diana.utils import get_fields, DEFAULT_FIELDS, DEFAULT_EXCLUDE
from admin_auto_filters.filters import AutocompleteFilter
from rangefilter.filters import NumericRangeFilter
from django.contrib.admin import EmptyFieldListFilter

from leaflet.admin import LeafletGeoAdminMixin, LeafletGeoAdmin
from leaflet_admin_list.admin import LeafletAdminListMixin

from django.conf import settings
from PIL import Image as ima
import os
import base64 
from io import StringIO


DEFAULT_LONGITUDE =  11.9900
DEFAULT_LATITUDE  = 42.2200
DEFAULT_ZOOM = 10
MAX_ZOOM = 16
MIN_ZOOM = 5

@admin.register(Place)
class PlaceAdmin(LeafletGeoAdmin, admin.ModelAdmin):
    display_raw = True
    list_display = ['name', 'subtitle', 'type', 'geometry', 'necropolis'] # 'parent_id'
    search_fields = ['name']
    filter_horizontal = ['tags']
    form = PlaceForm

    # overrides base setting of Leaflet Geo Widget
    settings_overrides = {
       'DEFAULT_CENTER': (DEFAULT_LATITUDE, DEFAULT_LONGITUDE),
       'DEFAULT_ZOOM': DEFAULT_ZOOM,
       'MAX_ZOOM': MAX_ZOOM,
       'MIN_ZOOM': MIN_ZOOM
    }


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']


@admin.register(Epoch)
class EpochAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']


@admin.register(TypeOfTomb)
class TypeOfTombAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']


@admin.register(TypeOfImage)
class TypeOfImageAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']


@admin.register(TypeOfDocument)
class TypeOfDocumentAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']


@admin.register(TypeOfObservation)
class TypeOfObservationAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']


class PlaceFilter(AutocompleteFilter):
    title = _('Place') # display title
    field_name = 'place' # name of the foreign key field


@admin.register(Image)
class ImageModel(admin.ModelAdmin):

    fields              = ['image_preview', *get_fields(Image, exclude=['id'])]
    readonly_fields     = ['iiif_file', 'uuid', 'image_preview', *DEFAULT_FIELDS]
    autocomplete_fields = ['tomb', 'author']
    list_display        = ['thumbnail_preview', 'title', 'tomb']
    search_fields       = ['title', 'tomb__name', 'type_of_image__text']
    list_filter         = [PlaceFilter]
    
    list_per_page = 10

    def image_preview(self, obj):
        return format_html(f'<img src="{settings.IIIF_URL}{obj.iiif_file}/full/full/0/default.jpg" height="300" />')

    def thumbnail_preview(self, obj):
        return format_html(f'<img src="{settings.IIIF_URL}{obj.iiif_file}/full/full/0/default.jpg" height="100" />')


@admin.register(Layer)
class LayerAdmin(admin.ModelAdmin):
    list_display = [*get_fields(Layer, exclude=['id'])]
    search_fields = ['title']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['lastname', 'firstname']# [*get_fields(Author, exclude=['id'])]
    search_fields = ['firstname', 'lastname']


@admin.register(Object3DHop)
class Object3DHopAdmin(admin.ModelAdmin):
    list_display = ['title', 'tomb', 'scaled', 'preview_image'] # [*get_fields(Object3DHop, exclude=['id', 'author'])]
    search_fields = ['title', 'place__name', 'type']


@admin.register(ObjectPointCloud)
class ObjectPointCloudAdmin(admin.ModelAdmin):
    list_display = ['title', 'tomb', 'scaled', 'preview_image'] # [*get_fields(ObjectPointCloud, exclude=['id', 'author'])]
    search_fields = ['title', 'place__name', 'type']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'size']# [*get_fields(Document, exclude=['id', 'type', 'place'])]
    search_fields = ['title', 'place__name', 'type']
    filter_horizontal = ['place']


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ['title', 'place', 'author']#[*get_fields(Observation, exclude=['id', 'type'])]
    search_fields = ['title', 'place__name', 'type']


@admin.register(Necropolis)
class NecropolisAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']


@admin.register(Technique3D)
class Technique3DAdmin(admin.ModelAdmin):
    list_display = [*get_fields(Technique3D, exclude=['id'])]
    search_fields = ['title', 'place__name', 'type']