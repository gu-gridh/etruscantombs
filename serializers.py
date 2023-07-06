from diana.abstract.serializers import DynamicDepthSerializer, GenericSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from . import models
from diana.utils import get_fields, DEFAULT_FIELDS
from .models import *


class PlaceSerializer(DynamicDepthSerializer):

    class Meta:
        model = Place
        fields = ['id']+get_fields(Place, exclude=DEFAULT_FIELDS+['min_year', 'max_year'])


class PlaceGeoSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Place
        fields = ['id']+get_fields(Place, exclude=DEFAULT_FIELDS)
        geo_field = 'geometry'
        depth = 1


class FocusSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Focus
        fields = ['id']+get_fields(Focus, exclude=DEFAULT_FIELDS)
        geo_field = 'place'
        depth = 1

class TIFFImageSerializer(DynamicDepthSerializer):

    class Meta:
        model = Image
        fields = ['id']+get_fields(Image, exclude=DEFAULT_FIELDS)


class VideoSerializer(DynamicDepthSerializer):

    class Meta:
        model = Video
        fields = ['id']+get_fields(Video, exclude=DEFAULT_FIELDS)


class ObservationSerializer(DynamicDepthSerializer):

    class Meta:
        model = Observation
        fields = ['id']+get_fields(Observation, exclude=DEFAULT_FIELDS)


class RePhotographySerializer(DynamicDepthSerializer):

    class Meta:
        model = RePhotography
        fields = ['id']+get_fields(RePhotography, exclude=DEFAULT_FIELDS)
