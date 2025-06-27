from rest_framework import serializers

from Accountapp.models import *

class AddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddonTable
        fields = [
            'id',
            'item',
            'name',
            'description',
            'image',
            'price',
            'created_at',
            'updated_at',
        ]

class ItemSerializer(serializers.ModelSerializer):
    addons = AddonSerializer(many=True, read_only=True)

    class Meta:
        model = ItemTable
        fields = [
            'id',
            'name',
            'category',
            'subcategory',
            'type',
            'image',
            'description',
            'voice_description',
            'price',
            'quantity',
            'created_at',
            'updated_at',
            'fast_delivery',
            'newest',
            'addons',
        ]


class SubCategorySerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = SubCategoryTable
        fields = [
            'id',
            'category',
            'name',
            'created_at',
            'updated_at',
            'items',
        ]


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
    items = ItemSerializer(many=True, read_only=True)  # Optional: all items under this category

    class Meta:
        model = CategoryTable
        fields = [
            'id',
            'name',
            'created_at',
            'updated_at',
            'subcategories',
            'items',
        ]

# class ItemBriefSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ItemTable
#         fields = ['id', 'name', 'price']


class OfferTableSerializer(serializers.ModelSerializer):
    itemid = ItemSerializer(read_only=True)

    class Meta:
        model = OfferTable
        fields = [
            'id',
            'name',
            'startdate',
            'enddate',
            'offer_percentage',
            'itemid',
            'offerdescription',
            'createdat',
            'updatedat',
        ]

class OrderTableSerializer(serializers.ModelSerializer):
    userid = serializers.PrimaryKeyRelatedField(queryset=LoginTable.objects.all())
    deliveryid = serializers.PrimaryKeyRelatedField(
        queryset=LoginTable.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = OrderTable
        fields = [
            'id',
            'userid',
            'totalamount',
            'orderstatus',
            'paymentstatus',
            'deliveryid',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_deliveryid(self, value):
        if value:
            allowed_roles = value.user_roles.values_list('role', flat=True)
            if 'DELIVERY' not in allowed_roles and 'WAITER' not in allowed_roles:
                raise serializers.ValidationError("Delivery person must be a Waiter or Delivery Boy.")
        return value