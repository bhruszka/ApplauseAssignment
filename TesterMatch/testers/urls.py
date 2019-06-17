from django.urls import path

from .views import match_testers, DeviceList

urlpatterns = [
    path('match-testers/', match_testers, name='match_testers'),
    path('devices/', DeviceList.as_view(), name='device_list'),
]
