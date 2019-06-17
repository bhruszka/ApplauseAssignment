from rest_framework import serializers
from .models import Tester, Device


class TesterSerializer(serializers.ModelSerializer):
    experience = serializers.IntegerField()

    class Meta:
        model = Tester
        fields = ('experience', 'first_name', 'last_name', 'country')


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('description', 'id')
