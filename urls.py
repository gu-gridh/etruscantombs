from django.urls import path, include
from rest_framework import routers
from . import views
import diana.utils as utils


router = routers.DefaultRouter()
endpoint = utils.build_app_endpoint("jubileum")
documentation = utils.build_app_api_documentation("jubileum", endpoint)

router.register(rf'{endpoint}/geojson/place', views.PlaceGeoViewSet, basename='place on geojson')
router.register(rf'{endpoint}/image', views.IIIFImageViewSet, basename='image')

urlpatterns = [
    path('', include(router.urls)),

    # Automatically generated views
    *utils.get_model_urls('jubileum', endpoint, 
        exclude=['image', 'place']),

    *utils.get_model_urls('jubileum', f'{endpoint}', exclude=['image', 'place']),
    *documentation
]