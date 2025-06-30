from rest_framework import serializers

from Accountapp.models import *
from Accountapp.serializer import LoginTableSerializer


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
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    subsubcategory_name = serializers.CharField(source='subsubcategory.name', read_only=True)

    class Meta:
        model = ItemTable
        fields = [
            'id',
            'name',
            'category',
            'category_name',
            'subcategory',
            'subcategory_name',
            'subsubcategory',
            'subsubcategory_name',
            'is_veg',
            'image',
            'description',
            'voice_description',
            'price',
            'quantity',
            'created_at',
            'updated_at',
            'fast_delivery',
            'newest',
        ]


class CategorySerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = CategoryTable
        fields = [
            'id',
            'name',
            'created_at',
        ]

class SubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoryTable.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = SubCategoryTable
        fields = ['id', 'name', 'category', 'category_id', 'created_at']

class SubSubCategorySerializer(serializers.ModelSerializer):
    subcategory = SubCategorySerializer(read_only=True)

    class Meta:
        model = SubSubCategoryTable
        fields = ['id', 'name', 'subcategory', 'created_at']

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
    
class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponTable
        fields = [
            'id',
            'code',
            'description',
            'discount_percentage',
            'max_discount_amount',
            'min_order_amount',
            'valid_from',
            'valid_to',
            'is_active',
            'usage_limit',
            'used_count',
        ]

class VoucherSerializer(serializers.ModelSerializer):
    userid = LoginTableSerializer(read_only=True)

    class Meta:
        model = VoucherTable
        fields = [
            'id',
            'code',
            'description',
            'value',
            'valid_from',
            'valid_to',
            'is_active',
            'userid',
            'used',
            'used_at',
        ]

class BranchTableSerializer(serializers.ModelSerializer):
    managers = serializers.PrimaryKeyRelatedField(
        many=True, queryset=LoginTable.objects.all(), required=False
    )

    class Meta:
        model = BranchTable
        fields = [
            'id',
            'name',
            'place',
            'address',
            'phone',
            'latitude',
            'longitude',
            'floors',
            'managers',
            'created_at',
            'updated_at',
        ]

class FloorTableSerializer(serializers.ModelSerializer):
    branch = BranchTableSerializer()

    class Meta:
        model = FloorTable
        fields = ['id', 'branch', 'floor_number', 'name', 'description']