from unittest.mock import DEFAULT
from . import models, serializers
from django.db.models import Q
from diana.abstract.views import DynamicDepthViewSet, GeoViewSet
from diana.abstract.models import get_fields, DEFAULT_FIELDS
from django.db.models import Q
from django.http import HttpResponse
import json

DEBUG_UNKNOWN_ID = 1  # sets correct IDs for epochs

class PlaceGeoViewSet(GeoViewSet):

    # queryset = models.Place.objects.all().order_by('id')
    serializer_class = serializers.PlaceGeoSerializer

    def get_serializer(self, *args, **kwargs):
        # Get depth parameter from the URL query parameters (e.g., ?depth=3)
        depth = self.request.query_params.get('depth', None)

        if depth is not None:
            try:
                depth = int(depth)  # Convert to integer
            except ValueError:
                depth = None  # If depth is invalid, we don't apply any depth

        # Pass the depth to the serializer if it's provided
        if depth:
            kwargs['depth'] = depth

        return super(PlaceGeoViewSet, self).get_serializer(*args, **kwargs)

    filterset_fields = [
        field for field in get_fields(
            models.Place,
            exclude=DEFAULT_FIELDS + ['geometry', 'threedhop_count', 'pointcloud_count', 'threejs_count']
        ) if field != 'name'
    ]
    search_fields = ['placename'] 
    bbox_filter_field = 'geometry'
    bbox_filter_include_overlapping = True

    def get_queryset(self):
        queryset = models.Place.objects.all().order_by('id')
        name = self.request.query_params.get('name')
        with_3D = self.request.query_params.get('with_3D')
        with_plan = self.request.query_params.get('with_plan')
        with_panorama = self.request.query_params.get('with_panorama')
        site = self.request.query_params.get('site')
        show_unknown = self.request.query_params.get('show_unknown')
        unknown_id = DEBUG_UNKNOWN_ID
        minyear = self.request.query_params.get('minyear')
        maxyear = self.request.query_params.get('maxyear')
        
        if name:
            queryset = queryset.filter(name__iexact=name)

        if with_3D:
            queryset = queryset.filter(Q(object_3Dhop__isnull=False)| Q(object_pointcloud__isnull=False) | Q(object_threejs__isnull=False)).distinct()
        if with_plan:
            queryset = queryset.filter(Q(images__type_of_image__text__exact="floor plan") | Q(images__type_of_image__text__exact="section")).distinct()
        if with_panorama:
            queryset = queryset.filter(Q(panorama__isnull=False)).distinct()
        if site:
            queryset = queryset.filter(Q(necropolis__site=site)).distinct()
            
        if minyear and maxyear and show_unknown:
            if show_unknown == 'true':
                queryset_dated = queryset.filter(Q(min_year__lte=minyear) & Q(max_year__gte=maxyear))
                queryset_unknown = queryset.filter(Q(epoch__id=unknown_id))
                queryset = queryset_dated | queryset_unknown
            else:
                queryset = queryset.filter(Q(min_year__lte=minyear) & Q(max_year__gte=maxyear)).distinct()
        elif minyear and maxyear:
            queryset = queryset.filter(Q(min_year__lte=minyear) & Q(max_year__gte=maxyear)).distinct()
            
        if show_unknown and not minyear and not maxyear:
            if show_unknown == 'true':      
                queryset = queryset.filter(Q(epoch_id=unknown_id))
        
        return queryset
        


class TombsInfoViewSet(DynamicDepthViewSet):

    serializer_class = serializers.PlaceSerializer

    def list(self, request):
        # Query Parameters 
        with_3D = self.request.query_params.get('with_3D')
        with_plan = self.request.query_params.get('with_plan')
        with_panorama = self.request.query_params.get('with_panorama')
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
            places = places.filter(Q(object_3Dhop__isnull=False)| Q(object_pointcloud__isnull=False) | Q(object_threejs__isnull=False)).distinct()
        
        if with_plan:
            places = places.filter(Q(images__type_of_image__text__exact="floor plan") 
                                  |Q(images__type_of_image__text__exact="section"))

        if with_panorama:
            places = places.filter(Q(panorama__isnull=False))
        
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
        hidden_tombs = all_tombs - tombs_shown

        tombs_shown_id = places.values_list('id', flat=True)

        plans_count =  models.Image.objects.filter(Q(tomb__id__in=list(tombs_shown_id)) & 
                                                   (Q(type_of_image__text__icontains="floor plan") | Q(type_of_image__text__icontains="section"))).distinct().count()
        #places.filter(id__in=list(
         #                   models.Image.objects.filter(Q(type_of_image__text__icontains="floor plan") 
          #                                            | Q (type_of_image__text__icontains="section"))
           #                                             .values_list('tomb', flat=True))).count()
        
        photographs_count = models.Image.objects.filter(Q(tomb__id__in=list(tombs_shown_id)) & Q(type_of_image__text__icontains="photograph")).distinct().count()
        #places.filter(id__in=list(
         #                   models.Image.objects.filter(type_of_image__text__icontains="photograph").values_list('tomb', flat=True))
          #                  ).count()
        

        threedhop_count = models.Object3DHop.objects.filter(tomb__id__in=list(tombs_shown_id)).distinct().count() # places.filter(id__in=list(models.Object3DHop.objects.all().values_list('tomb', flat=True))).count()
        pointcloud_count = models.ObjectPointCloud.objects.filter(tomb__id__in=list(tombs_shown_id)).distinct().count() #places.filter(id__in=list(models.ObjectPointCloud.objects.all().values_list('tomb', flat=True))).count()
        threejs_count = models.Object3js.objects.filter(tomb__id__in=list(tombs_shown_id)).distinct().count() # places.filter(id__in=list(models.Object3js.objects.all().values_list('tomb', flat=True))).count()
        objects_3d = threedhop_count + pointcloud_count + threejs_count
        panorama_count = models.Panorama.objects.filter(tomb__id__in=list(tombs_shown_id)).distinct().count()# places.filter(id__in=list(models.Panorama.objects.all().values_list('tomb', flat=True))).count()
        
        data = {
            'all_tombs': all_tombs,
            'shown_tombs': tombs_shown,
            'hidden_tombs': hidden_tombs,
            'photographs': photographs_count,
            'drawing': plans_count,
            'objects_3d' : objects_3d,
            'panoramas' : panorama_count
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
        with_panorama = self.request.query_params.get('with_panorama')
        oldest_epoch = self.request.query_params.get('oldest_epoch')
        newest_epoch = self.request.query_params.get('newest_epoch')
        show_unknown = self.request.query_params.get('show_unknown')
        minyear = self.request.query_params.get('minyear')
        maxyear = self.request.query_params.get('maxyear')
        site = self.request.query_params.get('site')
        
        if with_3D:
            queryset = queryset.filter(Q(object_threejs__isnull=False)| Q(object_pointcloud__isnull=False)| Q(object_3Dhop__isnull=False)).distinct()
        if with_plan:
            queryset = queryset.filter(Q(images__type_of_image__text__exact="floor plan") | Q(images__type_of_image__text__exact="section")).distinct()
        if with_panorama:
            queryset = queryset.filter(Q(panorama__isnull=False)).distinct()
            
        if site:
            queryset = queryset.filter(Q(necropolis__site=site)).distinct()
        
        unknown_id = DEBUG_UNKNOWN_ID
        
        if oldest_epoch and newest_epoch and show_unknown:
            lower = min(oldest_epoch, newest_epoch)
            higher = max(oldest_epoch, newest_epoch)
            
            # this is quite specific to how the data is currently saved in the database:
            # id = 1 : Unknown
            # id = 5 : 700-650 BC
            # id = 6 : 625-400 BC
            # id = 7 : 400-200 BC
            
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


class BoundingBoxView(GeoViewSet):
    # serializer_class = serializers.PlaceCoordinatesSerializer
    # serializer_class = serializers.PlaceSerializer
    # queryset = models.Place.objects.all().order_by('id')
    # filterset_fields = get_fields(models.Place, exclude=DEFAULT_FIELDS + ['geometry'])
    
    def list(self, request):
        queryset = models.Place.objects.all().order_by('id')
        with_3D = self.request.query_params.get('with_3D')
        with_plan = self.request.query_params.get('with_plan')
        with_panorama = self.request.query_params.get('with_panorama')
        oldest_epoch = self.request.query_params.get('oldest_epoch')
        newest_epoch = self.request.query_params.get('newest_epoch')
        show_unknown = self.request.query_params.get('show_unknown')
        minyear = self.request.query_params.get('minyear')
        maxyear = self.request.query_params.get('maxyear')
        site = self.request.query_params.get('site')
        necropolis = self.request.query_params.get('necropolis')
        type_of_tomb = self.request.query_params.get('type')
        dataset = self.request.query_params.get('dataset')
        
        if with_3D:
            queryset = queryset.filter(Q(object_3Dhop__isnull=False)| Q(object_pointcloud__isnull=False) | Q(object_threejs__isnull=False)).distinct()
        if with_plan:
            queryset = queryset.filter(Q(images__type_of_image__text__exact="floor plan") | Q(images__type_of_image__text__exact="section")).distinct()
        if with_panorama:
            queryset = queryset.filter(Q(panorama__isnull=False))    
        if site:
            queryset = queryset.filter(Q(necropolis__site=site)).distinct()
            
        if necropolis:
            queryset = queryset.filter(Q(necropolis=necropolis))
            
        if type_of_tomb:
            queryset = queryset.filter(Q(type=type_of_tomb))
            
        if dataset:
            queryset = queryset.filter(Q(dataset=dataset))
        
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
        
        bounding_box = {
            "min_latitude": None,
            "min_longitude": None,
            "max_latitude": None,
            "max_longitude": None
        }
        
        all_lat = []
        all_lon = []
        for tomb in queryset:
            lon, lat = tomb.geometry.coords
            all_lat.append(lat)
            all_lon.append(lon)
        
        if len(all_lat) > 0 and len(all_lon) > 0:
            bounding_box["min_latitude"] = min(all_lat)
            bounding_box["min_longitude"] = min(all_lon)
            bounding_box["max_latitude"] = max(all_lat)
            bounding_box["max_longitude"] = max(all_lon)
            
        return HttpResponse(json.dumps(bounding_box))



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

class Object3jsViewSet(DynamicDepthViewSet):
    
    queryset = models.Object3js.objects.all()
    serializer_class = serializers.Object3jsSerializer
    filterset_fields = get_fields(models.Object3js, exclude=DEFAULT_FIELDS+['preview_image', 'camera_position', 'look_at'])

class PanoramaViewSet(DynamicDepthViewSet):
    
    queryset = models.Panorama.objects.all()
    serializer_class = serializers.PanoramaSerializer
    filterset_fields = get_fields(models.Panorama, exclude=DEFAULT_FIELDS+['preview_image', 'start_position'])


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

    def get_queryset(self):
        queryset = models.Dataset.objects.all().order_by('short_name')
        tomb_id = self.request.query_params.get('tomb', None)

        if tomb_id is not None: 
            queryset = queryset.filter(tomb__pk__exact=tomb_id).distinct()


        return queryset


class DatasetPerTombViewSet(DynamicDepthViewSet):
    
    queryset = models.Dataset.objects.all().order_by('short_name')
    serializer_class = serializers.DatasetSerializer
    filterset_fields = get_fields(models.Dataset, exclude=DEFAULT_FIELDS)

    def get_queryset(self):
        queryset = models.Dataset.objects.all().order_by('short_name')
        tomb_id = self.request.query_params.get('tomb', None)

        if tomb_id is not None:
            attached_datasets = set()
            if models.Place.objects.filter(pk__exact = tomb_id).exists():

                tomb_of_interest = models.Place.objects.filter(pk__exact = tomb_id)[0]
                # find images connected to tomb
                for image in tomb_of_interest.images.all():
                    attached_datasets.add(image.dataset.pk)
                
                # find textured meshes connected to tomb
                for texturedmesh in tomb_of_interest.object_3js.all():
                    attached_datasets.add(texturedmesh.dataset.pk)
                    
                # find detailed meshes connected to tomb
                for detailedmesh in tomb_of_interest.object_3Dhop.all():
                    attached_datasets.add(detailedmesh.dataset.pk)

                # find pointclouds connected to tomb
                for pointcloud in tomb_of_interest.object_pointcloud.all():
                    attached_datasets.add(pointcloud.dataset.pk)

                # find documents connected to tomb
                for document in tomb_of_interest.documentation.all():
                    attached_datasets.add(document.dataset.pk)

                # find observations connected to tomb
                for observation in tomb_of_interest.observation.all():
                    attached_datasets.add(observation.dataset.pk)

                queryset = queryset.filter(pk__in = attached_datasets).distinct()
            else:
                queryset = models.Dataset.objects.none()

        return queryset