from django.urls import path, include
from rest_framework import routers
from . import views
import diana.utils as utils


router = routers.DefaultRouter()
endpoint = utils.build_app_endpoint("etruscantombs")
documentation = utils.build_app_api_documentation("etruscantombs", endpoint)

router.register(rf'{endpoint}/geojson/place', views.PlaceGeoViewSet, basename='place on geojson')
router.register(rf'{endpoint}/image', views.IIIFImageViewSet, basename='image')
router.register(rf'{endpoint}/document', views.DocumentViewSet, basename='document')
router.register(rf'{endpoint}/object3dhop', views.Object3DHopViewSet, basename='object 3D hop')
router.register(rf'{endpoint}/objectpointcloud', views.ObjectPointcloudViewSet, basename='object point cloud')
router.register(rf'{endpoint}/necropolis', views.NecropolisViewSet, basename='necropolis')
router.register(rf'{endpoint}/coordinates', views.PlaceCoordinatesViewSet, basename='coordinates')

urlpatterns = [
    path('', include(router.urls)),

    # Automatically generated views
    *utils.get_model_urls('etruscantombs', endpoint, 
        exclude=['image', 'place', 'document', 'object3dhop', 'objectpointcloud', 'necropolis', 'coordinates']),

    *utils.get_model_urls('etruscantombs', f'{endpoint}', exclude=['image', 'place', 'document', 'object3dhop', 'objectpointcloud', 'necropolis', 'coordinates']),
    *documentation
]