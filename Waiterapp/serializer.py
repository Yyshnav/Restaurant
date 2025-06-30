from rest_framework import serializers
from Accountapp.models import WaiterTable

class WaiterTableSerializer(serializers.ModelSerializer):
    userid = serializers.LoginTableSerializer()

    class Meta:
        model = WaiterTable
        fields = [
            'id',
            'userid',
            'name',
            'phone',
            'image',
            'address',
            'idproof',
            'created_at',
        ]