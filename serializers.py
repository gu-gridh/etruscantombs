from diana.abstract.serializers import DynamicDepthSerializer, GenericSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework.serializers import SerializerMethodField
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

    # images = TIFFImageSerializer(many=True)
    photographs_count = SerializerMethodField()
    plans_count = SerializerMethodField()
    threedhop_count = SerializerMethodField()
    pointcloud_count = SerializerMethodField()
    first_photograph_id = SerializerMethodField()
    
    class Meta:
        model = Place
        fields = get_fields(Place, exclude=DEFAULT_FIELDS)+ ['id', 'photographs_count', 'plans_count', 'threedhop_count', 'pointcloud_count', 'first_photograph_id']
        geo_field = 'geometry'
        depth = 1
            
    def get_photographs_count(self, obj):
        return obj.images.filter(type_of_image__text="photograph").count()
        
    def get_plans_count(self, obj):
        floor_plans = obj.images.filter(type_of_image__text="floor plan").count()
        section_plans = obj.images.filter(type_of_image__text="section").count()
        return floor_plans + section_plans
    
    def get_threedhop_count(self, obj):
        return obj.object_3Dhop.count()
    
    def get_pointcloud_count(self, obj):
        return obj.object_pointcloud.count()
    
    def get_first_photograph_id(self, obj):
        
        try: 
            object_to_display = obj.images.filter(type_of_image__text="photograph").filter(published=True).values()[0]
        except:
            object_to_display = []
        
        return object_to_display

class PlaceCoordinatesSerializer(GeoFeatureModelSerializer):
        
    class Meta:
        model = Place
        fields = ['id', 'name', 'dataset']
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
        
        
class DatasetSerializer(DynamicDepthSerializer):

    class Meta:
        model = Dataset
        fields = get_fields(Dataset, exclude=DEFAULT_FIELDS)+ ['id']


class Object3DHopSerializer(DynamicDepthSerializer):
    
    class Meta:
        model = Object3DHop
        fields = get_fields(Object3DHop, exclude=DEFAULT_FIELDS)+ ['id']


class ObjectPointCloudSerializer(DynamicDepthSerializer):

    class Meta:
        model = ObjectPointCloud
        fields = get_fields(ObjectPointCloud, exclude=DEFAULT_FIELDS)+ ['id']


class DocumentSerializer(DynamicDepthSerializer):
    type_names = SerializerMethodField()
    
    class Meta:
        model = Document
        fields = get_fields(Document, exclude=DEFAULT_FIELDS)+ ['id', 'type_names']

    def get_type_names(self, obj):
        type_names = []
        types = obj.type.all()
        for type in types:
            type_names.append(type.text)
        return type_names
    
    
class ObservationSerializer(DynamicDepthSerializer):

    class Meta:
        model = Observation
        fields = get_fields(Observation, exclude=DEFAULT_FIELDS)+ ['id']
        
        
class NecropolisSerializer(DynamicDepthSerializer):

    class Meta:
        model = Necropolis
        fields = get_fields(Necropolis, exclude=DEFAULT_FIELDS)+ ['id']
        

class SiteSerializer(DynamicDepthSerializer):

    class Meta:
        model = Site
        fields = get_fields(Site, exclude=DEFAULT_FIELDS)+ ['id']