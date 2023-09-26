from unittest.mock import DEFAULT
from . import models, serializers
from django.db.models import Prefetch, Q
from diana.abstract.views import DynamicDepthViewSet, GeoViewSet
from diana.abstract.models import get_fields, DEFAULT_FIELDS


class PlaceGeoViewSet(GeoViewSet):

    queryset = models.Place.objects.all().order_by('id')
    serializer_class = serializers.PlaceGeoSerializer
    filterset_fields = get_fields(models.Place, exclude=DEFAULT_FIELDS + ['geometry'])
    search_fields = ['placename']
    bbox_filter_field = 'geometry'
    bbox_filter_include_overlapping = True


class IIIFImageViewSet(DynamicDepthViewSet):
    """
    retrieve:
    Returns a single image instance.

    list:
    Returns a list of all the existing images in the database, paginated.

    count:
    Returns a count of the existing images after the application of any filter.
    """
    
    queryset = models.Image.objects.all().order_by('id')
    serializer_class = serializers.TIFFImageSerializer
    filterset_fields = get_fields(models.Image, exclude=DEFAULT_FIELDS + ['iiif_file', 'file'])


class LayerViewSet(DynamicDepthViewSet):
    
    queryset = models.Layer.objects.all()
    serializer_class = serializers.LayerSerializer
    filterset_fields = get_fields(models.Layer, exclude=DEFAULT_FIELDS)


class Object3DHopViewSet(DynamicDepthViewSet):
    
    queryset = models.Object3DHop.objects.all()
    serializer_class = serializers.Object3DHopSerializer
    filterset_fields = get_fields(models.Object3DHop, exclude=DEFAULT_FIELDS)


class ObjectPointcloudViewSet(DynamicDepthViewSet):
    
    queryset = models.ObjectPointCloud.objects.all()
    serializer_class = serializers.ObjectPointCloudSerializer
    filterset_fields = get_fields(models.ObjectPointCloud, exclude=DEFAULT_FIELDS)


class DocumentViewSet(DynamicDepthViewSet):
    
    queryset = models.Document.objects.all()
    serializer_class = serializers.DocumentSerializer
    filterset_fields = get_fields(models.Document, exclude=DEFAULT_FIELDS+['upload'])
    

class ObservationViewSet(DynamicDepthViewSet):
    
    queryset = models.Observation.objects.all()
    serializer_class = serializers.ObservationSerializer
    filterset_fields = get_fields(models.Observation, exclude=DEFAULT_FIELDS)