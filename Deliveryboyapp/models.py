from rest_framework import serializers
from Accountapp import serializer
from Accountapp.models import DeliveryBoyTable

class DeliveryBoyTableSerializer(serializers.ModelSerializer):
    userid = serializer.LoginTableSerializer(read_only=True)

    class Meta:
        model = DeliveryBoyTable
        fields = '__all__'



