from rest_framework import serializers
from .models import Tester


class TesterSerializer(serializers.ModelSerializer):
    experience = serializers.IntegerField()

    class Meta:
        model = Tester
        fields = ('experience', 'first_name', 'last_name', 'country')
