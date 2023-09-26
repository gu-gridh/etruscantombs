from diana.abstract.serializers import DynamicDepthSerializer, GenericSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer, ListSerializer
from . import models
from diana.utils import get_fields, DEFAULT_FIELDS
from .models import *


class PlaceSerializer(DynamicDepthSerializer):

    class Meta:
        model = Place
        fields = get_fields(Place, exclude=DEFAULT_FIELDS)+ ['id']


class TIFFImageSerializer(DynamicDepthSerializer):

    class Meta:
        model = Image
        fields = get_fields(Image, exclude=DEFAULT_FIELDS)+ ['id']
        

class PlaceGeoSerializer(GeoFeatureModelSerializer):

    images = TIFFImageSerializer(many=True)
    
    class Meta:
        model = Place
        fields = get_fields(Place, exclude=DEFAULT_FIELDS)+ ['id', 'images']
        geo_field = 'geometry'
        depth = 1



class LayerSerializer(DynamicDepthSerializer):

    class Meta:
        model = Layer
        fields = get_fields(Layer, exclude=DEFAULT_FIELDS)+ ['id']


class AuthorSerializer(DynamicDepthSerializer):

    class Meta:
        model = Author
        fields = get_fields(Author, exclude=DEFAULT_FIELDS)+ ['id']

class Object3DHopSerializer(DynamicDepthSerializer):

    class Meta:
        model = Object3DHop
        fields = get_fields(Object3DHop, exclude=DEFAULT_FIELDS)+ ['id']


class ObjectPointCloudSerializer(DynamicDepthSerializer):

    class Meta:
        model = ObjectPointCloud
        fields = get_fields(ObjectPointCloud, exclude=DEFAULT_FIELDS)+ ['id']


class DocumentSerializer(DynamicDepthSerializer):

    class Meta:
        model = Document
        fields = get_fields(Document, exclude=DEFAULT_FIELDS)+ ['id']


class ObservationSerializer(DynamicDepthSerializer):

    class Meta:
        model = Observation
        fields = get_fields(Observation, exclude=DEFAULT_FIELDS)+ ['id']