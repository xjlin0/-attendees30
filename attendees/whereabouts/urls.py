from django.urls import path, include
from rest_framework import routers

from attendees.whereabouts.views import (
    api_user_division_viewset,
)

app_name = "whereabouts"

router = routers.DefaultRouter()
router.register(
    'api/user_divisions',
    api_user_division_viewset,
    basename='division',
)

urlpatterns = [
    path('', include(router.urls)),
]
