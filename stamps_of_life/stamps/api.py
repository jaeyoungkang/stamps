from .models import Stamp
from rest_framework import serializers, viewsets

class StampSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stamp
        fields = '__all__'

class StampViewSet(viewsets.ModelViewSet):
    queryset = Stamp.objects.all()
    serializer_class = StampSerializer
