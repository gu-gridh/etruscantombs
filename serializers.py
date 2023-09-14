from diana.abstract.serializers import DynamicDepthSerializer, GenericSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from . import models
from diana.utils import get_fields, DEFAULT_FIELDS
from .models import *


class PlaceSerializer(DynamicDepthSerializer):

    class Meta:
        model = Place
        fields = get_fields(Place, exclude=DEFAULT_FIELDS)+ ['id']


class PlaceGeoSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Place
        fields = get_fields(Place, exclude=DEFAULT_FIELDS)+ ['id']
        geo_field = 'geometry'
        depth = 1


class TIFFImageSerializer(DynamicDepthSerializer):

    class Meta:
        model = Image
        fields = get_fields(Image, exclude=DEFAULT_FIELDS)+ ['id']


class LayerSerializer(DynamicDepthSerializer):

    class Meta:
        model = Layer
        fields = get_fields(Layer, exclude=DEFAULT_FIELDS)+ ['id']


class AuthorSerializer(DynamicDepthSerializer):

    class Meta:
        model = Author
        fields = get_fields(Author, exclude=DEFAULT_FIELDS)+ ['id']

class Object3DSerializer(DynamicDepthSerializer):

    class Meta:
        model = Object3D
        fields = get_fields(Object3D, exclude=DEFAULT_FIELDS)+ ['id']


class FloorPlanSerializer(DynamicDepthSerializer):

    class Meta:
        model = FloorPlan
        fields = get_fields(FloorPlan, exclude=DEFAULT_FIELDS)+ ['id']


class DocumentSerializer(DynamicDepthSerializer):

    class Meta:
        model = Document
        fields = get_fields(Document, exclude=DEFAULT_FIELDS)+ ['id']


class ObservationSerializer(DynamicDepthSerializer):

    class Meta:
        model = Observation
        fields = get_fields(Observation, exclude=DEFAULT_FIELDS)+ ['id']