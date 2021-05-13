from django.urls import path, include
from rest_framework import routers

from attendees.whereabouts.views import (
    api_datagrid_data_place_viewset,
    api_all_state_view_set,
    api_all_address_view_set,
    api_user_division_viewset,
    api_user_place_view_set,
)

app_name = "whereabouts"

router = routers.DefaultRouter()
router.register(
    'api/user_divisions',
    api_user_division_viewset,
    basename='division',
)
router.register(
    'api/user_places',
    api_user_place_view_set,
    basename='place',
)
router.register(
    'api/datagrid_data_place/(?P<place_id>.+)',
    api_datagrid_data_place_viewset,
    basename='place',
)
router.register(
    'api/all_addresses',
    api_all_address_view_set,
    basename='address',
)
router.register(
    'api/all_states',
    api_all_state_view_set,
    basename='address',
)

urlpatterns = [
    path('', include(router.urls)),
]
