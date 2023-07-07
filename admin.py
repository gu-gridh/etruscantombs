from django.contrib import admin
from django.contrib.gis.db import models
from .models import *
from django.utils.html import format_html
from django.contrib.gis import admin
from django.utils.translation import gettext_lazy as _
from diana.utils import get_fields, DEFAULT_FIELDS, DEFAULT_EXCLUDE
from admin_auto_filters.filters import AutocompleteFilter
from rangefilter.filters import NumericRangeFilter
from django.contrib.admin import EmptyFieldListFilter
from django.conf import settings


DEFAULT_LONGITUDE =  12.1096
DEFAULT_LATITUDE  = 42.4209
DEFAULT_ZOOM = 10

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = get_fields(Role) 
    search_fields = ['role']

# Register your models here.
@admin.register(Creator)
class CreatorAdmin(admin.ModelAdmin):
    # fields              = get_fields(Creator, exclude=['id'])
    # readonly_fields     = [*DEFAULT_FIELDS]
    list_display = ["name"]
    autocomplete_fields =['role']
    search_fields = ['name', 'role']
    

@admin.register(Tomb)
class TombAdmin(admin.GISModelAdmin):

    fields              = get_fields(Tomb, exclude=['id'])
    readonly_fields     = [*DEFAULT_FIELDS]
    list_display = ['name', 'necropolis', 'geometry', 'description', 'comment']
    search_fields = ['name', 'necropolis']
    autocomplete_fields = ['tag']

    gis_widget_kwargs = {
        'attrs': {
            'default_lon' : DEFAULT_LONGITUDE,
            'default_lat' : DEFAULT_LATITUDE,
            'default_zoom' : DEFAULT_ZOOM,
        },
    }

@admin.register(Necropolis)
class NecropolisAdmin(admin.GISModelAdmin):

    fields              = get_fields(Necropolis, exclude=['id'])
    readonly_fields     = [*DEFAULT_FIELDS]
    list_display = ['name', 'geometry', 'description', 'comment']
    search_fields = ['name']
    autocomplete_fields = ['tag']

    gis_widget_kwargs = {
        'attrs': {
            'default_lon' : DEFAULT_LONGITUDE,
            'default_lat' : DEFAULT_LATITUDE,
            'default_zoom' : DEFAULT_ZOOM,
        },
    }


@admin.register(ImageTypeTag)
class ImageTypeTagAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']


@admin.register(Focus)
class FocusAdmin(admin.GISModelAdmin):
    list_display = ['name', 'place', 'text']
    search_fields = ['name', 'text']

    gis_widget_kwargs = {
        'attrs': {
            'default_lon' : DEFAULT_LONGITUDE,
            'default_lat' : DEFAULT_LATITUDE,
            'default_zoom' : DEFAULT_ZOOM,
        },
    }


@admin.register(Image)
class ImageModel(admin.ModelAdmin):

    fields              = ['image_preview', *get_fields(Image, exclude=['id'])]
    readonly_fields     = ['iiif_file', 'uuid', 'image_preview', *DEFAULT_FIELDS]
    autocomplete_fields = ['photographer', 'tomb', 'tag', 'focus', 'type']
    list_display = ['title', 'thumbnail_preview', 'photographer', 'tomb', 'date', 'description', 'type']
    search_fields = ['title', 'photographer', 'tomb', 'date', 'type']

    list_per_page = 10

    def image_preview(self, obj):
        return format_html(f'<img src="{settings.IIIF_URL}{obj.iiif_file}/full/full/0/default.jpg" height="300" />')
    
    def thumbnail_preview(self, obj):
        return format_html(f'<img src="{settings.IIIF_URL}{obj.iiif_file}/full/full/0/default.jpg" height="100" />')


@admin.register(RePhotography)
class RePhotographyAdmin(admin.ModelAdmin):
    list_display = ['old_image', 'new_image']


@admin.register(Video)
class VideoModel(admin.ModelAdmin):
    autocomplete_fields = ['photographer', 'tomb', 'tag', 'focus']
    list_display = ['title', 'photographer', 'tomb', 'link', 'date', 'description']
    search_fields = ['title', 'photographer', 'tomb', 'date']


@admin.register(Observation)
class ObservationModel(admin.ModelAdmin):
    autocomplete_fields = ['creator', 'tomb', 'tag', 'focus']
    list_display = ['title', 'creator', 'tomb', 'date', 'description']
    search_fields = ['title', 'creator', 'tomb', 'date']
