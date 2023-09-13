from django.contrib.gis.db import models
from .models import *
from django.utils.html import format_html
from django.contrib.gis import admin
from django.utils.translation import gettext_lazy as _
from diana.utils import get_fields, DEFAULT_FIELDS, DEFAULT_EXCLUDE
from admin_auto_filters.filters import AutocompleteFilter
from rangefilter.filters import NumericRangeFilter
from django.contrib.admin import EmptyFieldListFilter

from leaflet.admin import LeafletGeoAdminMixin
from leaflet_admin_list.admin import LeafletAdminListMixin

from django.conf import settings
from PIL import Image as ima
import os
import base64 
from io import StringIO


DEFAULT_LONGITUDE =  11.99
DEFAULT_LATITUDE  = 42.22
DEFAULT_ZOOM = 10

@admin.register(Place)
class PlaceAdmin(LeafletGeoAdminMixin, admin.ModelAdmin,):
    display_raw = True
    list_display = ['name', 'geometry', 'parent_id']
    search_fields = ['name']

    gis_widget_kwargs = {
        'attrs': {
            'default_lon' : DEFAULT_LONGITUDE,
            'default_lat' : DEFAULT_LATITUDE,
            'default_zoom' : DEFAULT_ZOOM,
        },
    }


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']


class PlaceFilter(AutocompleteFilter):
    title = _('Place') # display title
    field_name = 'place' # name of the foreign key field

@admin.register(Image)
class ImageModel(admin.ModelAdmin):

    fields              = ['image_preview', *get_fields(Image, exclude=['id'])]
    readonly_fields     = ['iiif_file', 'uuid', 'image_preview', *DEFAULT_FIELDS]
    autocomplete_fields = ['place']
    list_display        = ['thumbnail_preview', 'title', 'place']
    search_fields       = ['title', 'place__name', 'type']
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
    list_display = [*get_fields(Author, exclude=['id'])]
    search_fields = ['author_firstname', 'author_lastname']


@admin.register(Object3D)
class Object3DAdmin(admin.ModelAdmin):
    list_display = [*get_fields(Object3D, exclude=['id'])]
    search_fields = ['title', 'place__name', 'type']
