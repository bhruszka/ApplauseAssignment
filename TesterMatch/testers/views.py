from django.db.models import Count, Q, F
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from testers.serializers import TesterSerializer, DeviceSerializer
from .models import Tester, SUPPORTED_COUNTRIES, Device

SUPPORTED_COUNTRIES_VALUES = [c[0] for c in SUPPORTED_COUNTRIES]

# Values needed for generating swagger schema
testers_response = openapi.Response('response description', TesterSerializer(many=True))

devices_param = openapi.Parameter('devices', openapi.IN_QUERY,
                                  description="devices for which experience should be calculated, empty means all",
                                  type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))
countries_param = openapi.Parameter('countries', openapi.IN_QUERY,
                                    description="countries from which testers should be included, empty means any",
                                    type=openapi.TYPE_ARRAY,
                                    explode=True,
                                    items=openapi.Items(type=openapi.TYPE_STRING, enum=SUPPORTED_COUNTRIES_VALUES),)


@swagger_auto_schema(method='get', manual_parameters=[devices_param, countries_param],
                     responses={200: testers_response},
                     operation_description='Returns list of testers ordered by experience')
@api_view(['GET'])
def match_testers(request):
    query_countries = request.GET.getlist('countries')
    query_devices = request.GET.getlist('devices')

    # Accepting different formats of array in query params
    query_countries = [c for q_c in query_countries for c in q_c.split(',')]
    query_devices = [d for q_d in query_devices for d in q_d.split(',')]

    # Checking if all countries in query parameters are valid
    if not all([c in SUPPORTED_COUNTRIES_VALUES for c in query_countries]):
        return Response('Query parameter \'countries\' has invalid value', status=status.HTTP_400_BAD_REQUEST)

    # Checking if all device ids in query parameters are valid
    if query_devices and not Device.objects.filter(id__in=query_devices).count() == len(query_devices):
        return Response('Query parameter \'devices\' has invalid value', status=status.HTTP_400_BAD_REQUEST)

    query_set = Tester.objects
    query_set = query_set.filter(country__in=query_countries) if query_countries else query_set.all()

    if query_devices:
        query_set = query_set.annotate(
            experience=Count('bug', filter=(Q(bug__device__in=F('devices')) & Q(bug__device__in=query_devices))))
    else:
        query_set = query_set.annotate(
            experience=Count('bug', filter=(Q(bug__device__in=F('devices')))))

    serializer = TesterSerializer(query_set.order_by('-experience', 'last_name', 'first_name'), many=True)
    return Response(serializer.data)


class DeviceList(generics.ListAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
