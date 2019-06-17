from django.db.models import Count, Q, F
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from testers.serializers import TesterSerializer
from .models import Tester, SUPPORTED_COUNTRIES_VALUES, Device


@api_view(['GET'])
def match_testers(request):
    query_countries = request.GET.getlist('countries')
    query_devices = request.GET.getlist('devices')

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


# country = openapi.Parameter('country', openapi.IN_QUERY, description="test manual param", type=openapi.TYPE_ARRAY)
