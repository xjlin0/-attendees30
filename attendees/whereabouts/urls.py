from django.urls import path, include
from rest_framework import routers

from attendees.whereabouts.views import (
    api_user_division_viewset,
    api_user_contact_view_set,
)

app_name = "whereabouts"

router = routers.DefaultRouter()
router.register(
    'api/user_divisions',
    api_user_division_viewset,
    basename='division',
)
router.register(
    'api/user_contacts',
    api_user_contact_view_set,
    basename='contact',
)

urlpatterns = [
    path('', include(router.urls)),
]
