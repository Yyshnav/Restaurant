from rest_framework import serializers
from django.contrib.auth import get_user_model

from Accountapp.models import CartTable, ItemTable, ProfileTable, RatingTable, WishlistTable
from Accountapp.serializer import LoginTableSerializer
from Adminapp.serializer import AddonSerializer, ItemSerializer

LoginTable = get_user_model()

class ProfileTableSerializer(serializers.ModelSerializer):
    loginid = serializers.PrimaryKeyRelatedField(queryset=LoginTable.objects.all())

    class Meta:
        model = ProfileTable
        fields = [
            'id',
            'name',
            'phone',
            'image',
            'dob',
            'latitude',
            'longitude',
            'place',
            'loginid',
            'created_at',
            'updated_at'
        ]

class RatingTableSerializer(serializers.ModelSerializer):
    # Read-only nested fields
    userid = ProfileTableSerializer(read_only=True)
    itemid = ItemSerializer(read_only=True)

    # Write-only fields for creation/updating
    userid_id = serializers.PrimaryKeyRelatedField(
        queryset=LoginTable.objects.all(), write_only=True, source='userid'
    )
    itemid_id = serializers.PrimaryKeyRelatedField(
        queryset=ItemTable.objects.all(), write_only=True, source='itemid', allow_null=True, required=False
    )

    class Meta:
        model = RatingTable
        fields = [
            'id',
            'userid',       
            'userid_id',     
            'itemid',       
            'itemid_id',     
            'rating_type',
            'rating',
            'comment',
            'createdat',
            'updatedat',
        ]

class CartTableSerializer(serializers.ModelSerializer):
    userid = LoginTableSerializer(read_only=True)
    fooditem = ItemSerializer(read_only=True)
    addon = AddonSerializer(read_only=True)

    class Meta:
        model = CartTable
        fields = [
            'id',
            'userid',
            'fooditem',
            'quantity',
            'price',
            'addon',
            'instruction',
            'added_at',
            'updated_at',
            'total_price',
        ]


class WishlistSerializer(serializers.ModelSerializer):
    fooditem_name = serializers.CharField(source='fooditem.name', read_only=True)
    fooditem_image = serializers.CharField(source='fooditem.image_url', read_only=True)
    fooditem_price = serializers.DecimalField(source='fooditem.price', read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = WishlistTable
        fields = ['id', 'fooditem', 'fooditem_name', 'fooditem_image', 'fooditem_price', 'added_at']
        read_only_fields = ['id', 'added_at', 'fooditem_name', 'fooditem_image', 'fooditem_price']