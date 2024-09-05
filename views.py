from unittest.mock import DEFAULT
from . import models, serializers
from django.db.models import Q
from diana.abstract.views import DynamicDepthViewSet, GeoViewSet
from diana.abstract.models import get_fields, DEFAULT_FIELDS
from django.db.models import Q
from django.http import HttpResponse
import json

DEBUG_UNKNOWN_ID = 1  # it's 4 for debugging

class PlaceGeoViewSet(GeoViewSet):

    # queryset = models.Place.objects.all().order_by('id')
    serializer_class = serializers.PlaceGeoSerializer
    filterset_fields = get_fields(models.Place, exclude=DEFAULT_FIELDS + ['geometry', 'threedhop_count', 'pointcloud_count'])
    search_fields = ['placename'] # this does nothing!!
    bbox_filter_field = 'geometry'
    bbox_filter_include_overlapping = True
    
    def get_queryset(self):
        queryset = models.Place.objects.all().order_by('id')
        with_3D = self.request.query_params.get('with_3D')
        with_plan = self.request.query_params.get('with_plan')
        
        if with_3D:
            queryset = queryset.filter(Q(object_3Dhop__isnull=False)| Q(object_pointcloud__isnull=False)).distinct()
        if with_plan:
            queryset = queryset.filter(Q(images__type_of_image__text__exact="floor plan") | Q(images__type_of_image__text__exact="section")).distinct()
        
        return queryset
        


class TombsInfoViewSet(DynamicDepthViewSet):

    serializer_class = serializers.PlaceSerializer

    def list(self, request):
        # Query Parameters 
        with_3D = self.request.query_params.get('with_3D')
        with_plan = self.request.query_params.get('with_plan')
        period = self.request.query_params.get('epoch')
        necropolis = self.request.query_params.get('necropolis')
        type_of_tomb = self.request.query_params.get('type')
        oldest_epoch = self.request.query_params.get('oldest_epoch')
        newest_epoch = self.request.query_params.get('newest_epoch')
        show_unknown = self.request.query_params.get('show_unknown')
        minyear = self.request.query_params.get('minyear')
        maxyear = self.request.query_params.get('maxyear')
        dataset = self.request.query_params.get('dataset')
        site = self.request.query_params.get('site')

        # Filtering places 
        all_tombs = models.Place.objects.all().count()
        places = models.Place.objects.all()
        
        if dataset:
            places = places.filter(Q(dataset__id__exact=dataset))
        
        if with_3D:
            places = places.filter(Q(object_3Dhop__isnull=False)| Q(object_pointcloud__isnull=False))
        
        if with_plan:
            places = places.filter(Q(images__type_of_image__text__exact="floor plan") 
                                  |Q(images__type_of_image__text__exact="section"))
        
        if period:
            places = places.filter(epoch__id=period)           

        if necropolis:
            places = places.filter(necropolis__id=necropolis)
            
        if site:
            places = places.filter(necropolis__site=site)

        if type_of_tomb:
            places = places.filter(type__id=type_of_tomb)
            
        unknown_id = DEBUG_UNKNOWN_ID
        
        if oldest_epoch and newest_epoch and show_unknown:
            lower = min(oldest_epoch, newest_epoch)
            higher = max(oldest_epoch, newest_epoch)
            
            # this is quite specific to how the data is currently coded:
            # id = 1 : Unknown (4 for debugging)
            # id = 5 : 700-650 BC
            # id = 6 : 625-400 BC
            # id = 7 : 400-200 BC
            
            # thus if looking for oldest = 5 and newest = 7, it should return all numbers >= 5 and <= 7

            if show_unknown == 'true':
                places = places.filter(Q(epoch__id__gte=lower) & Q(epoch__id__lte=higher) | Q(epoch_id=unknown_id)).distinct()
            else:
                places = places.filter(Q(epoch__id__gte=lower) & Q(epoch__id__lte=higher)).distinct()
        elif oldest_epoch and newest_epoch:
            lower = min(oldest_epoch, newest_epoch)
            higher = max(oldest_epoch, newest_epoch)
            places = places.filter(Q(epoch__id__gte=lower) & Q(epoch__id__lte=higher)).distinct() 
        # elif show_unknown:
        #     if show_unknown == 'true':      
        #         places = places.filter(Q(epoch_id=unknown_id)).distinct()
        
        if minyear and maxyear and show_unknown:
            if show_unknown == 'true':
                queryset_dated = places.filter(Q(min_year__lte=minyear) & Q(max_year__gte=maxyear))
                queryset_unknown = places.filter(Q(epoch__id=unknown_id))
                places = queryset_dated | queryset_unknown
            else:
                places = places.filter(Q(min_year__lte=minyear) & Q(max_year__gte=maxyear)).distinct()
        elif minyear and maxyear:
            places = places.filter(Q(min_year__lte=minyear) & Q(max_year__gte=maxyear)).distinct()
            
        if show_unknown and not minyear and not oldest_epoch:
            if show_unknown == 'true':      
                places = places.filter(Q(epoch_id=unknown_id))
            
        tombs_shown = places.all().count()
        hidden_tombs = all_tombs -  tombs_shown

        plans_count =  places.filter(id__in=list(
                            models.Image.objects.filter(Q(type_of_image__text__icontains="floor plan") 
                                                      | Q (type_of_image__text__icontains="section"))
                                                        .values_list('tomb', flat=True))).count()
        
        photographs_count = places.filter(id__in=list(
                            models.Image.objects.filter(type_of_image__text__icontains="photograph").values_list('tomb', flat=True))
                            ).count()
        

        threedhop_count = places.filter(id__in=list(models.Object3DHop.objects.all().values_list('tomb', flat=True))).count()
        pointcloud_count = places.filter(id__in=list(models.ObjectPointCloud.objects.all().values_list('tomb', flat=True))).count()
        objects_3d = threedhop_count + pointcloud_count
        
        data = {
            'all_tombs': all_tombs,
            'shown_tombs': tombs_shown,
            'hidden_tombs': hidden_tombs,
            'photographs': photographs_count,
            'drawing': plans_count,
            'objects_3d' : objects_3d
        }

        return HttpResponse(json.dumps(data))
    

class PlaceCoordinatesViewSet(GeoViewSet):
    serializer_class = serializers.PlaceCoordinatesSerializer
    queryset = models.Place.objects.all().order_by('id')
    filterset_fields = get_fields(models.Place, exclude=DEFAULT_FIELDS + ['geometry'])
    
    def get_queryset(self):
        queryset = models.Place.objects.all().order_by('id')
        with_3D = self.request.query_params.get('with_3D')
        with_plan = self.request.query_params.get('with_plan')
        oldest_epoch = self.request.query_params.get('oldest_epoch')
        newest_epoch = self.request.query_params.get('newest_epoch')
        show_unknown = self.request.query_params.get('show_unknown')
        minyear = self.request.query_params.get('minyear')
        maxyear = self.request.query_params.get('maxyear')
        site = self.request.query_params.get('site')
        
        if with_3D:
            queryset = queryset.filter(Q(object_3Dhop__isnull=False)| Q(object_pointcloud__isnull=False)).distinct()
        if with_plan:
            queryset = queryset.filter(Q(images__type_of_image__text__exact="floor plan") | Q(images__type_of_image__text__exact="section")).distinct()
            
        if site:
            queryset = queryset.filter(Q(necropolis__site=site)).distinct()
        
        unknown_id = DEBUG_UNKNOWN_ID
        
        if oldest_epoch and newest_epoch and show_unknown:
            lower = min(oldest_epoch, newest_epoch)
            higher = max(oldest_epoch, newest_epoch)
            
            # this is quite specific to how the data is currently coded:
            # id = 1 : Unknown
            # id = 5 : 700-650 BC
            # id = 6 : 625-400 BC
            # id = 7 : 400-200 BC
            
            # thus if looking for oldest = 5 and newest = 7, it should return all numbers >= 5 and <= 7

            if show_unknown == 'true':
                queryset = queryset.filter(Q(epoch__id__gte=lower) & Q(epoch__id__lte=higher) | Q(epoch_id=unknown_id)).distinct()
            else:
                queryset = queryset.filter(Q(epoch__id__gte=lower) & Q(epoch__id__lte=higher)).distinct()
        elif oldest_epoch and newest_epoch:
            lower = min(oldest_epoch, newest_epoch)
            higher = max(oldest_epoch, newest_epoch)
            queryset = queryset.filter(Q(epoch__id__gte=lower) & Q(epoch__id__lte=higher)).distinct() 
        
        if minyear and maxyear and show_unknown:
            if show_unknown == 'true':
                queryset_dated = queryset.filter(Q(min_year__lte=minyear) & Q(max_year__gte=maxyear))
                queryset_unknown = queryset.filter(Q(epoch__id=unknown_id))
                queryset = queryset_dated | queryset_unknown
            else:
                queryset = queryset.filter(Q(min_year__lte=minyear) & Q(max_year__gte=maxyear)).distinct()
        elif minyear and maxyear:
            queryset = queryset.filter(Q(min_year__lte=minyear) & Q(max_year__gte=maxyear)).distinct()
            
        if show_unknown and not minyear and not oldest_epoch:
            if show_unknown == 'true':      
                queryset = queryset.filter(Q(epoch_id=unknown_id))
        
        return queryset


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
    filterset_fields = get_fields(models.Object3DHop, exclude=DEFAULT_FIELDS+['preview_image', 'trackball_start', 
                                                                              'start_angle', 'start_pan', 
                                                                              'min_max_phi', 'min_max_theta'])


class ObjectPointcloudViewSet(DynamicDepthViewSet):
    
    queryset = models.ObjectPointCloud.objects.all()
    serializer_class = serializers.ObjectPointCloudSerializer
    filterset_fields = get_fields(models.ObjectPointCloud, exclude=DEFAULT_FIELDS+['preview_image', 'camera_position', 'look_at'])


class DocumentViewSet(DynamicDepthViewSet):
    
    queryset = models.Document.objects.all()
    serializer_class = serializers.DocumentSerializer
    filterset_fields = get_fields(models.Document, exclude=DEFAULT_FIELDS+['upload'])
    

class ObservationViewSet(DynamicDepthViewSet):
    
    queryset = models.Observation.objects.all()
    serializer_class = serializers.ObservationSerializer
    filterset_fields = get_fields(models.Observation, exclude=DEFAULT_FIELDS)


class NecropolisViewSet(DynamicDepthViewSet):
    
    queryset = models.Necropolis.objects.all().order_by('text')
    serializer_class = serializers.NecropolisSerializer
    filterset_fields = get_fields(models.Necropolis, exclude=DEFAULT_FIELDS+['geometry'])
    

class SiteViewSet(DynamicDepthViewSet):
    
    queryset = models.Site.objects.all().order_by('text')
    serializer_class = serializers.SiteSerializer
    filterset_fields = get_fields(models.Site, exclude=DEFAULT_FIELDS)
    
    
class DatasetViewSet(DynamicDepthViewSet):
    
    queryset = models.Dataset.objects.all().order_by('short_name')
    serializer_class = serializers.DatasetSerializer
    filterset_fields = get_fields(models.Dataset, exclude=DEFAULT_FIELDS)