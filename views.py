from unittest.mock import DEFAULT
from . import models, serializers
from django.db.models import Prefetch, Q
from itertools import chain
from diana.abstract.views import DynamicDepthViewSet, GeoViewSet
from diana.abstract.models import get_fields, DEFAULT_FIELDS


class PlaceViewSet(DynamicDepthViewSet):
    serializer_class = serializers.PlaceSerializer
    filterset_fields = get_fields(models.Place, exclude=DEFAULT_FIELDS + ['geometry'])
    search_fields = ['placename']

    def dispatch(self, request, *args, **kwargs):
        model_name = request.GET.get('type')
        if model_name == 'image':
            self.model_type = models.Image
        elif model_name == 'video':
            self.model_type = models.Video
        elif model_name == 'observation':
            self.model_type = models.Observation

        return super(PlaceViewSet, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # queryset = models.Place.objects.all()
        model_type = self.request.query_params.get('type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if model_type:
            if model_type == 'art' or model_type== 'drawing':
                objects_type = models.Image.objects.all().filter(type__text__icontains=model_type)

                if start_date and end_date:
                    objects_type = objects_type.filter(date__year__gte=start_date, date__year__lte=end_date)
                elif start_date:
                    objects_type = objects_type.filter(date__year__gte=start_date)
                elif end_date:
                    objects_type = objects_type.filter(date__year__lte=end_date)
                else:
                    objects_type = objects_type.all()

                queryset = models.Place.objects.all().filter(id__in=list(objects_type.values_list('place', flat=True)))
                
            else:
                objects_type = self.model_type.objects.all()

                if start_date and end_date:
                    objects_type = objects_type.filter(date__year__gte=start_date, date__year__lte=end_date)
                elif start_date:
                    objects_type = objects_type.filter(date__year__gte=start_date)
                elif end_date:
                    objects_type = objects_type.filter(date__year__lte=end_date)
                else:
                    objects_type = objects_type.all()

                queryset = models.Place.objects.all().filter(id__in=list(objects_type.values_list('place', flat=True)))

        else:
            if start_date and end_date:
                queryset = models.Place.objects.all().filter(
                    Q(id__in=list(models.Image.filter(date__year__gte=start_date, date__year__lte=end_date).values_list('place', flat=True)))
                    |Q(id__in=list(models.Video.filter(date__year__gte=start_date, date__year__lte=end_date).values_list('place', flat=True)))
                    |Q(id__in=list(models.Observation.filter(date__year__gte=start_date, date__year__lte=end_date).values_list('place', flat=True)))
                )
            elif start_date:
                queryset = models.Place.objects.all().filter(
                    Q(id__in=list(models.Image.filter(date__year__gte=start_date).values_list('place', flat=True)))
                    |Q(id__in=list(models.Video.filter(date__year__gte=start_date).values_list('place', flat=True)))
                    |Q(id__in=list(models.Observation.filter(date__year__gte=start_date).values_list('place', flat=True)))
                )
            elif end_date:
                queryset = models.Place.objects.all().filter(
                    Q(id__in=list(models.Image.filter(date__year__lte=end_date).values_list('place', flat=True)))
                    |Q(id__in=list(models.Video.filter(date__year__lte=end_date).values_list('place', flat=True)))
                    |Q(id__in=list(models.Observation.filter(date__year__lte=end_date).values_list('place', flat=True)))
                )
            else:
                queryset = models.Place.objects.all().filter(
                     Q(id__in=list(models.Image.objects.all().values_list('place', flat=True)))
                    |Q(id__in=list(models.Video.objects.all().values_list('place', flat=True)))
                    |Q(id__in=list(models.Observation.objects.all().values_list('place', flat=True)))
                )
                
        return queryset

class PlaceGeoViewSet(GeoViewSet):

    # queryset = models.Place.objects.all()
    serializer_class = serializers.PlaceGeoSerializer
    filterset_fields = get_fields(models.Place, exclude=DEFAULT_FIELDS + ['geometry'])
    search_fields = ['placename']
    bbox_filter_field = 'geometry'
    bbox_filter_include_overlapping = True

    def dispatch(self, request, *args, **kwargs):
        model_name = request.GET.get('type')
        if model_name == 'image':
            self.model_type = models.Image
        elif model_name == 'video':
            self.model_type = models.Video
        elif model_name == 'observation':
            self.model_type = models.Observation
        return super(PlaceGeoViewSet, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # queryset = models.Place.objects.all()
        model_type = self.request.query_params.get('type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if model_type:
            if model_type == 'art' or model_type== 'drawing':
                objects_type = models.Image.objects.all().filter(type__text__icontains=model_type)

                if start_date and end_date:
                    objects_type = objects_type.filter(date__year__gte=start_date, date__year__lte=end_date)
                elif start_date:
                    objects_type = objects_type.filter(date__year__gte=start_date)
                elif end_date:
                    objects_type = objects_type.filter(date__year__lte=end_date)
                else:
                    objects_type = objects_type.all()

                queryset = models.Place.objects.all().filter(id__in=list(objects_type.values_list('place', flat=True)))
                
            else:
                objects_type = self.model_type.objects.all()

                if start_date and end_date:
                    objects_type = objects_type.filter(date__year__gte=start_date, date__year__lte=end_date)
                elif start_date:
                    objects_type = objects_type.filter(date__year__gte=start_date)
                elif end_date:
                    objects_type = objects_type.filter(date__year__lte=end_date)
                else:
                    objects_type = objects_type.all()

                queryset = models.Place.objects.all().filter(id__in=list(objects_type.values_list('place', flat=True)))

        else:
            if start_date and end_date:
                queryset = models.Place.objects.all().filter(
                    Q(id__in=list(models.Image.objects.filter(date__year__gte=start_date, date__year__lte=end_date).values_list('place', flat=True)))
                    |Q(id__in=list(models.Video.objects.filter(date__year__gte=start_date, date__year__lte=end_date).values_list('place', flat=True)))
                    |Q(id__in=list(models.Observation.objects.filter(date__year__gte=start_date, date__year__lte=end_date).values_list('place', flat=True)))
                )
            elif start_date:
                queryset = models.Place.objects.all().filter(
                    Q(id__in=list(models.Image.objects.filter(date__year__gte=start_date).values_list('place', flat=True)))
                    |Q(id__in=list(models.Video.objects.filter(date__year__gte=start_date).values_list('place', flat=True)))
                    |Q(id__in=list(models.Observation.objects.filter(date__year__gte=start_date).values_list('place', flat=True)))
                )
            elif end_date:
                queryset = models.Place.objects.all().filter(
                    Q(id__in=list(models.Image.objects.filter(date__year__lte=end_date).values_list('place', flat=True)))
                    |Q(id__in=list(models.Video.objects.filter(date__year__lte=end_date).values_list('place', flat=True)))
                    |Q(id__in=list(models.Observation.objects.filter(date__year__lte=end_date).values_list('place', flat=True)))
                )
            else:
                queryset = models.Place.objects.all().filter(
                     Q(id__in=list(models.Image.objects.all().values_list('place', flat=True)))
                    |Q(id__in=list(models.Video.objects.all().values_list('place', flat=True)))
                    |Q(id__in=list(models.Observation.objects.all().values_list('place', flat=True)))
                )
                
        return queryset

class FocusGeoViewSet(GeoViewSet):

    serializer_class = serializers.FocusSerializer
    # queryset = models.Focus.objects.all()
    queryset = models.Focus.objects.all().filter(id__in=list(models.Image.objects.all().values_list('focus', flat=True)))
    filterset_fields = get_fields(models.Focus, exclude=DEFAULT_FIELDS + ['place'])
    search_fields = ['name']
    bbox_filter_field = 'place'

# Create your views here.
class IIIFImageViewSet(DynamicDepthViewSet):
    """
    retrieve:
    Returns a single image instance.

    list:
    Returns a list of all the existing images in the database, paginated.

    count:
    Returns a count of the existing images after the application of any filter.
    """
    queryset = models.Image.objects.all()
    serializer_class = serializers.TIFFImageSerializer
    filterset_fields = get_fields(models.Image, exclude=DEFAULT_FIELDS + ['iiif_file', 'file'])


class VideoViewSet(DynamicDepthViewSet):
    
    queryset = models.Video.objects.all()
    serializer_class = serializers.VideoSerializer
    filterset_fields = get_fields(models.Video, exclude=DEFAULT_FIELDS)


class ObservationViewSet(DynamicDepthViewSet):
    
    queryset = models.Observation.objects.all()
    serializer_class = serializers.ObservationSerializer
    filterset_fields = get_fields(models.Observation, exclude=DEFAULT_FIELDS+['document'])

class RePhotographyViewSet(DynamicDepthViewSet):
    
    # queryset = models.RePhotography.objects.all()
    serializer_class = serializers.RePhotographySerializer
    filterset_fields = get_fields(models.RePhotography, exclude=DEFAULT_FIELDS)


    def get_queryset(self):
        queryset = models.RePhotography.objects.all()
        if self.request.query_params.get('place'):
            place_id = self.request.query_params.get('place')
            queryset = models.RePhotography.objects.filter(old_image__place=place_id)
            
        return queryset
    

class TypeSearchViewSet(DynamicDepthViewSet):
    serializer_class = serializers.TIFFImageSerializer

    def get_queryset(self):
        q = self.request.GET["image_type"]
        queryset = models.Image.objects.filter(type__text__icontains=q)
        return queryset
    
    filterset_fields = ['id']+get_fields(models.Image, exclude=DEFAULT_FIELDS + ['iiif_file', 'file'])


class TagSearchViewSet(GeoViewSet):
    serializer_class = serializers.PlaceGeoSerializer
    filterset_fields = get_fields(models.Place, exclude=DEFAULT_FIELDS + ['geometry'])
    search_fields = ['placename']
    bbox_filter_field = 'geometry'
    bbox_filter_include_overlapping = True

    def get_queryset(self):
        q = self.request.GET["tag_set"]
        queryset = models.Place.objects.all().filter(Q(id__in=list(models.Image.objects.filter(tag__text__icontains=q).values_list('place', flat=True)))|
                                                    Q(id__in=list(models.Video.objects.filter(tag__text__icontains=q).values_list('place', flat=True))) |
                                                    Q(id__in=list(models.Observation.objects.filter(tag__text__icontains=q).values_list('place', flat=True))))
        return queryset

    
class RephotographyFocusSearch(DynamicDepthViewSet):
    serializer_class = serializers.RePhotographySerializer
    filterset_fields = get_fields(models.RePhotography, exclude=DEFAULT_FIELDS)

    def get_queryset(self):
        focus_id = self.request.GET["focus_id"]
        queryset = models.RePhotography.objects.filter(new_image__focus=focus_id)
        return queryset
    