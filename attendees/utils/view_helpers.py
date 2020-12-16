import time

from django.shortcuts import _get_queryset
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied


def get_object_or_delayed_403(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except ObjectDoesNotExist:
        time.sleep(2)
        raise ObjectDoesNotExist
    except MultipleObjectsReturned:
        raise MultipleObjectsReturned
