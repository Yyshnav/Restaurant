from decimal import Decimal
from rest_framework import serializers
from django.contrib.auth import get_user_model
from sympy import Q
from django.core.exceptions import ObjectDoesNotExist

from Accountapp.models import AddressTable, BranchTable, CartTable, CouponTable, DeliveryTable, FeedbackTable, ItemTable, ItemVariantTable, OrderItemTable, OrderTable, ProfileTable, RatingTable, WishlistTable
from Accountapp.serializer import LoginTableSerializer
from Adminapp.serializer import AddonSerializer, ItemSerializer, ItemVariantSerializer, OrderTableSerializer
from Adminapp.serializer import AddonSerializer, ItemSerializer, OrderTableSerializer
# from Deliveryboyapp.serializer import DeliveryBoyTableSerializer

LoginTable = get_user_model()

class ProfileTableSerializer(serializers.ModelSerializer):
    loginid = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ProfileTable
        fields = [
            'id',
            'name',
            'phone',
            'image',
            'address',
            'dob',
            # 'place',
            'loginid',
            'created_at',
            'updated_at'
        ]

class RatingTableSerializer(serializers.ModelSerializer):
    userid = ProfileTableSerializer(read_only=True)
    itemid = ItemSerializer(read_only=True)

    userid_id = serializers.PrimaryKeyRelatedField(queryset=LoginTable.objects.all(), write_only=True, source='userid')
    itemid_id = serializers.PrimaryKeyRelatedField(queryset=ItemTable.objects.all(), write_only=True, source='itemid', allow_null=True, required=False)

    class Meta:
        model = RatingTable
        fields = [
            'id', 'userid', 'userid_id', 'itemid', 'itemid_id', 'rating_type',
            'rating', 'comment', 'createdat', 'updatedat'
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
    fooditem_details = ItemSerializer(source='fooditem', read_only=True)  # ✅ Correct source

    fooditem_id = serializers.PrimaryKeyRelatedField(
        queryset=ItemTable.objects.all(), source='fooditem', write_only=True
    )

    class Meta:
        model = WishlistTable
        fields = ['id', 'fooditem_id', 'fooditem_details', 'added_at']
        read_only_fields = ['id', 'added_at', 'fooditem_details']

   
class OrderItemTableSerializer(serializers.ModelSerializer):
    itemname = ItemSerializer(read_only=True)
    addon = AddonSerializer(read_only=True)
    variant = ItemVariantSerializer(read_only=True)

    class Meta:
        model = OrderItemTable
        fields = '__all__'
       

# class WishlistSerializer(serializers.ModelSerializer):
#     userid = LoginTableSerializer(read_only=True)
#     fooditem = ItemSerializer(read_only=True)

#     class Meta:
#         model = WishlistTable
        # fields = ['id', 'userid', 'fooditem', 'added_at']     

class CartSerializer(serializers.ModelSerializer):
    fooditem_name = serializers.CharField(source='fooditem.name', read_only=True)
    fooditem_price = serializers.FloatField(source='fooditem.price', read_only=True)
    addon_name = serializers.CharField(source='addon.name', read_only=True)
    is_veg = serializers.BooleanField(source='fooditem.is_veg', read_only=True)
    variant_name = serializers.SerializerMethodField()

    class Meta:
        model = CartTable
        fields = [
            'id', 'fooditem', 'fooditem_name', 'quantity', 'price', 'addon', 'addon_name','fooditem_price',
            'instruction', 'added_at', 'updated_at', 'total_price', 'variant_name', 'is_veg', 'variant_id'
        ]
        read_only_fields = ['id', 'added_at', 'updated_at', 'fooditem_name', 'addon_name']

    def get_variant_name(self, obj):
    # If your CartTable doesn't have a direct variant FK, you can skip or modify this.
        variant_qs = obj.fooditem.variants.all()
        return variant_qs[0].variant_name if variant_qs.exists() else None

class ProfileNameUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileTable
        fields = ['name']

class ProfileLocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileTable
        fields = '__all__'

class AddressTableSerializer(serializers.ModelSerializer):
    userid = LoginTableSerializer(read_only=True)

    class Meta:
        model = AddressTable
        fields = '__all__'

class DeliveryTableSerializer(serializers.ModelSerializer):
    order = OrderTableSerializer(read_only=True) 
    address= AddressTableSerializer(read_only=True)
    class Meta:
        model = DeliveryTable
        fields = ['id', 'userid', 'name','address', 'order', 'phone', 'instruction', 'created_at', 'updated_at']



class DeliveryTableSerializer(serializers.ModelSerializer):
    order = OrderTableSerializer(read_only=True) 
    address= AddressTableSerializer(read_only=True)
    class Meta:
        model = DeliveryTable
        fields = ['id', 'userid', 'name','address', 'order', 'phone', 'instruction', 'created_at', 'updated_at']



class FeedbackSerializer(serializers.ModelSerializer):
    userid = LoginTableSerializer(read_only=True)
    class Meta:
        model = FeedbackTable
        fields = [
            'id',
            'userid',
            'feedback',
            'rating',
            'created_at',
        ]


   
class AddressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressTable
        fields = [
            'id', 'name', 'phone', 'address', 'city', 'state', 'postal_code',
            'country', 'latitude', 'longitude', 'is_default'
        ]

class PlaceOrderSerializer(serializers.ModelSerializer):
    address = AddressTableSerializer(read_only=True)
    delivery = DeliveryTableSerializer(read_only=True)

    class Meta:
        model = OrderTable
        fields = [
            'id', 'userid', 'address', 'delivery', 'total_amount', 'status',
            'created_at', 'updated_at'
        ]

# class OrderItemSerializer(serializers.Serializer):
#     itemname_id = serializers.IntegerField()
#     fooditem_price = serializers.DecimalField(max_digits=10, decimal_places=2)
#     quantity = serializers.IntegerField()
#     variant_id = serializers.IntegerField(required=False, allow_null=True)
#     instruction = serializers.CharField(required=False, allow_blank=True)
#     addon_id = serializers.IntegerField(required=False, allow_null=True)

#     def validate(self, data):
#         item_id = data.get('item_id')
#         variant_id = data.get('variant_id')
#         addon_id = data.get('addon_id')

#         if not ItemTable.objects.filter(id=item_id).exists():
#             raise serializers.ValidationError(f"Item with id {item_id} does not exist.")
#         if variant_id and not ItemVariantTable.objects.filter(id=variant_id, item_id=item_id).exists():
#             raise serializers.ValidationError(f"Variant with id {variant_id} does not exist for item {item_id}.")
#         if addon_id and not ItemTable.objects.filter(id=addon_id).exists():
#             raise serializers.ValidationError(f"Addon with id {addon_id} does not exist.")
#         return data


class UserOrderItemSerializer(serializers.Serializer):
    # item_id = serializers.IntegerField()
    itemname = serializers.PrimaryKeyRelatedField(queryset=ItemTable.objects.all())
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    instruction = serializers.CharField(required=False, allow_blank=True)
    addon_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        item_id = data.get('itemname')
        variant_id = data.get('variant_id')
        addon_id = data.get('addon_id')

        if not ItemTable.objects.filter(id=item_id).exists():
            raise serializers.ValidationError(f"Item with id {item_id} does not exist.")
        if variant_id and not ItemVariantTable.objects.filter(id=variant_id, item_id=item_id).exists():
            raise serializers.ValidationError(f"Variant with id {variant_id} does not exist for item {item_id}.")
        if addon_id and not ItemTable.objects.filter(id=addon_id).exists():
            raise serializers.ValidationError(f"Addon with id {addon_id} does not exist.")
        
        return data

class UserOrderSerializer(serializers.ModelSerializer):
    items = UserOrderItemSerializer(many=True)
    coupon = serializers.PrimaryKeyRelatedField(queryset=CouponTable.objects.all(), required=False, allow_null=True)
    branch = serializers.PrimaryKeyRelatedField(queryset=BranchTable.objects.all())
    address = serializers.CharField(write_only=True)
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    userid = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderTable
        fields = [
            'latitude', 'longitude', 'items', 'payment_method', 'coupon',
            'branch', 'delivery_instructions', 'address', 'userid'
        ]

    def validate(self, data):
        # Validate items
        items = data.get('items', [])
        if not items:
            raise serializers.ValidationError("At least one item is required to place an order.")

        # Validate branch
        branch = data.get('branch')
        if not BranchTable.objects.filter(id=branch.id).exists():
            raise serializers.ValidationError(f"Branch with id {branch.id} does not exist.")

        # Validate coupon if provided
        coupon = data.get('coupon')
        if coupon and not CouponTable.objects.filter(id=coupon.id, is_active=True).exists():
            raise serializers.ValidationError(f"Coupon with id {coupon.id} does not exist or is inactive.")

        # Validate address fields
        if not data.get('address'):
            raise serializers.ValidationError("Address is required.")
        if data.get('latitude') is None or data.get('longitude') is None:
            raise serializers.ValidationError("Latitude and longitude are required.")

        # Validate userid
        userid = data.get('userid')
        if not LoginTable.objects.filter(id=userid, is_active=True).exists():
            raise serializers.ValidationError(f"User with id {userid} does not exist or is inactive.")

        return data

    def create(self, validated_data):
        request = self.context.get("request")
        items_data = validated_data.pop("items")
        address = validated_data.pop("address")
        latitude = validated_data.pop("latitude")
        longitude = validated_data.pop("longitude")
        coupon = validated_data.pop("coupon", None)
        branch = validated_data.pop("branch")
        userid = validated_data.pop("userid")

        # Verify user exists
        try:
            user = LoginTable.objects.get(id=userid, is_active=True)
            print(f"User verified: ID={user.id}, Username={user.username}")
        except ObjectDoesNotExist:
            print(f"User verification failed: ID={userid} does not exist or is inactive")
            raise serializers.ValidationError(f"User with id {userid} does not exist or is inactive.")

        # Verify branch exists
        try:
            branch_instance = BranchTable.objects.get(id=branch.id)
            print(f"Branch verified: ID={branch_instance.id}, Name={branch_instance.name}")
        except ObjectDoesNotExist:
            print(f"Branch verification failed: ID={branch.id} does not exist")
            raise serializers.ValidationError(f"Branch with id {branch.id} does not exist.")

        # Prepare address data
        address_data = {
            'address': address,
            'latitude': latitude,
            'longitude': longitude,
            'city': validated_data.get('city', 'Kozhikode'),
            'state': validated_data.get('state', 'Kerala'),
            'postal_code': validated_data.get('postal_code', '673004'),
            'country': validated_data.get('country', 'India'),
            'name': validated_data.get('name', user.username),
            'phone': validated_data.get('phone', user.phone or '')
        }

        # Check if address already exists
        try:
            address_instance = AddressTable.objects.filter(
                userid_id=userid,
                address=address_data['address']
            ).first()
            if not address_instance:
                address_instance = AddressTable.objects.create(
                    userid=user,
                    **address_data
                )
                print(f"Created new address: ID={address_instance.id}, Address={address_instance.address}")
            else:
                print(f"Reused existing address: ID={address_instance.id}, Address={address_instance.address}")
        except Exception as e:
            print(f"Address creation failed: {str(e)}")
            raise serializers.ValidationError(f"Failed to create or retrieve address: {str(e)}")

        # Create order
        try:
            order = OrderTable.objects.create(
                userid=user,
                branch=branch_instance,
                address=address_instance,
                coupon=coupon,
                latitude=latitude,
                longitude=longitude,
                payment_method=validated_data.get('payment_method'),
                delivery_instructions=validated_data.get('delivery_instructions', ''),
                phone_number=address_data['phone']
            )
            print(f"Created order: ID={order.id}, UserID={order.userid_id}, Branch={order.branch_id}, Address={order.address_id}, Coupon={order.coupon_id}")
        except Exception as e:
            print(f"Order creation failed: {str(e)}")
            raise serializers.ValidationError(f"Failed to create order: {str(e)}")

        # Create order items
        try:
            for item_data in items_data:
                item = ItemTable.objects.get(id=item_data['item_id'])
                order_item = OrderItemTable.objects.create(
                    order=order,
                    itemname=item,
                    price=item_data['price'],
                    quantity=str(item_data['quantity']),
                    variant_id=item_data.get('variant_id'),
                    instruction=item_data.get('instruction', ''),
                    addon_id=item_data.get('addon_id')
                )
                print(f"Created order item: ItemID={order_item.itemname_id}, Quantity={order_item.quantity}, Price={order_item.price}")
        except Exception as e:
            print(f"Order item creation failed: {str(e)}")
            raise serializers.ValidationError(f"Failed to create order item: {str(e)}")

        return order
    
# class TrackOrderSerializer(serializers.ModelSerializer):
#     deliveryid_phone = serializers.SerializerMethodField()
#     deliveryid_latitude = serializers.SerializerMethodField()
#     deliveryid_longitude = serializers.SerializerMethodField()
#     order_item = OrderItemSerializer(many=True, read_only=True)


#     class Meta:
#         model = OrderTable
#         fields = ['id', 'orderstatus', 'deliveryid_phone', 'deliveryid_latitude', 'deliveryid_longitude', 'items']

#     def get_deliveryid_phone(self, obj):
#         if obj.deliveryid:
#             return obj.deliveryid.phone_number
#         return None

#     def get_deliveryid_latitude(self, obj):
#         if obj.deliveryid:
#             return getattr(obj.deliveryid.deliveryboy, 'latitude', None)
#         return None

#     def get_deliveryid_longitude(self, obj):
#         if obj.deliveryid:
#             return getattr(obj.deliveryid.deliveryboy, 'longitude', None)
#         return None


# class TrackOrderSerializer(serializers.ModelSerializer):
#     deliveryid_phone = serializers.SerializerMethodField()
#     deliveryid_latitude = serializers.SerializerMethodField()
#     deliveryid_longitude = serializers.SerializerMethodField()
#     items = OrderItemSerializer(source='order_item', many=True, read_only=True)

#     class Meta:
#         model = OrderTable
#         fields = ['id', 'orderstatus', 'deliveryid_phone', 'deliveryid_latitude', 'deliveryid_longitude', 'items']

#     def get_deliveryid_phone(self, obj):
#         if obj.deliveryid:
#             return obj.deliveryid.phone_number
#         return None

#     def get_deliveryid_latitude(self, obj):
#         if obj.deliveryid:
#             return getattr(obj.deliveryid.deliveryboy, 'latitude', None)
#         return None

#     def get_deliveryid_longitude(self, obj):
#         if obj.deliveryid:
#             return getattr(obj.deliveryid.deliveryboy, 'longitude', None)
#         return None


# class TrackOrderSerializer(serializers.ModelSerializer):
#     delivery_details = DeliveryBoyTableSerializer(source='deliveryid', read_only=True)
#     items = OrderItemSerializer(source='order_item', many=True, read_only=True)

#     class Meta:
#         model = OrderTable
#         fields = [
#             'id',
#             'orderstatus',
#             'paymentstatus',
#             'subtotal',
#             'tax',
#             'discount',
#             'totalamount',
#             'latitude',
#             'longitude',
#             'phone_number',
#             'created_at',
#             'updated_at',
#             'delivery_details',
#             'items'
#         ]