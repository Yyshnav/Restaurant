from decimal import Decimal
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework import status
from django.contrib.auth import get_user_model
from sympy import Q
from django.core.exceptions import ObjectDoesNotExist

from Accountapp.models import *
from Accountapp.serializer import LoginTableSerializer
from Adminapp.serializer import AddonSerializer, ItemSerializer, ItemVariantSerializer, OrderTableSerializer
# from Adminapp.serializer import AddonSerializer, ItemSerializer, OrderTableSerializer
# from Deliveryboyapp.serializer import DeliveryBoyTableSerializer
from django.core.files.base import ContentFile
from pydub import AudioSegment
import os
import io

LoginTable = get_user_model()

class ProfileTableSerializer(serializers.ModelSerializer):
    loginid = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ProfileTable
        fields = [
            'id',
            'name',
            'phone',
            'email',
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


# class CartTableSerializer(serializers.ModelSerializer):
#     userid = LoginTableSerializer(read_only=True)
#     fooditem = ItemSerializer(read_only=True)
#     addon = AddonSerializer(read_only=True)

#     class Meta:
#         model = CartTable
#         fields = [
#             'id',
#             'userid',
#             'fooditem',
#             'quantity',
#             'price',
#             'addon',
#             'instruction',
#             'added_at',
#             'updated_at',
#             'total_price',
#         ]



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
        # 
class AddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddonTable
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    fooditem_name = serializers.CharField(source='fooditem.name', read_only=True)
    fooditem_price = serializers.SerializerMethodField()  # ✅ use method field
    addon = AddonSerializer(many=True, read_only=True)
    addon_name = serializers.SerializerMethodField()
    is_veg = serializers.BooleanField(source='fooditem.is_veg', read_only=True)
    variant_name = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()  # ✅ includes addons now

    class Meta:
        model = CartTable
        fields = '__all__'

    def get_addon_name(self, obj):
        return [a.name for a in obj.addon.all()]

    def get_variant_name(self, obj):
        return obj.variant.variant_name if obj.variant else None

    def get_fooditem_price(self, obj):
        # ✅ Use variant price if available, else base food item price
        if obj.variant:
            return obj.variant.price
        if obj.fooditem:
            return obj.fooditem.price
        return 0  # fallback if no fooditem

    def get_total_price(self, obj):
        # ✅ Base price (fooditem/variant)
        base_price = self.get_fooditem_price(obj)

        # ✅ Addons price
        addon_total = sum(addon.price for addon in obj.addon.all())

        # ✅ Apply quantity
        quantity = int(obj.quantity or 1)
        return (base_price + addon_total) * quantity



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

# class DeliveryTableSerializer(serializers.ModelSerializer):
#     order = OrderTableSerializer(read_only=True) 
#     address= AddressTableSerializer(read_only=True)
#     class Meta:
#         model = DeliveryTable
#         fields = ['id', 'userid', 'name','address', 'order', 'phone', 'instruction', 'created_at', 'updated_at']



class DeliveryTableSerializer(serializers.ModelSerializer):
    order = OrderTableSerializer(read_only=True) 
    address= AddressTableSerializer(read_only=True)
    class Meta:
        model = DeliveryTable
        fields = ['id', 'userid', 'name','address', 'order', 'phone', 'instruction', 'voice_instruction', 'created_at', 'updated_at']



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
        variant_id = data.get('variant_id') or None
        addon_id = data.get('addon_id')

        if not ItemTable.objects.filter(id=item_id.id).exists():
            raise serializers.ValidationError(f"Item with id {item_id} does not exist.")
        # if variant_id and not ItemVariantTable.objects.filter(id=variant_id, item_id=item_id).exists():
        #     raise serializers.ValidationError(f"Variant with id {variant_id} does not exist for item {item_id}.")
        variant = None
        if variant_id and variant_id != 0:
            try:
                variant = ItemVariantTable.objects.get(id=variant_id)
            except ItemVariantTable.DoesNotExist:
                return JsonResponse({"error": f"Variant with ID {variant_id} not found."},
                                    status=status.HTTP_400_BAD_REQUEST)
        # if addon_id and not ItemTable.objects.filter(id=addon_id).exists():
            # raise serializers.ValidationError(f"Addon with id {addon_id} does not exist.")
        if addon_id is not None:
            if not ItemTable.objects.filter(id=addon_id).exists():
                raise serializers.ValidationError(
                    f"Addon with id {addon_id} does not exist."
                )
        
        return data

# class UserOrderSerializer(serializers.ModelSerializer):
#     items = UserOrderItemSerializer(many=True)
#     coupon = serializers.PrimaryKeyRelatedField(queryset=CouponTable.objects.all(), required=False, allow_null=True)
#     branch = serializers.PrimaryKeyRelatedField(queryset=BranchTable.objects.all())
#     address = serializers.CharField(write_only=True)
#     latitude = serializers.FloatField(write_only=True)
#     longitude = serializers.FloatField(write_only=True)
#     userid = serializers.IntegerField(write_only=True)

#     class Meta:
#         model = OrderTable
#         fields = [
#             'latitude', 'longitude', 'items', 'payment_method', 'coupon',
#             'branch', 'delivery_instructions', 'address', 'userid'
#         ]

#     def validate(self, data):
#         # Validate items
#         items = data.get('items', [])
#         if not items:
#             raise serializers.ValidationError("At least one item is required to place an order.")

#         # Validate branch
#         branch = data.get('branch')
#         if not BranchTable.objects.filter(id=branch.id).exists():
#             raise serializers.ValidationError(f"Branch with id {branch.id} does not exist.")

#         # Validate coupon if provided
#         coupon = data.get('coupon')
#         if coupon and not CouponTable.objects.filter(id=coupon.id, is_active=True).exists():
#             raise serializers.ValidationError(f"Coupon with id {coupon.id} does not exist or is inactive.")

#         # Validate address fields
#         if not data.get('address'):
#             raise serializers.ValidationError("Address is required.")
#         if data.get('latitude') is None or data.get('longitude') is None:
#             raise serializers.ValidationError("Latitude and longitude are required.")

#         # Validate userid
#         userid = data.get('userid')
#         if not LoginTable.objects.filter(id=userid, is_active=True).exists():
#             raise serializers.ValidationError(f"User with id {userid} does not exist or is inactive.")

#         return data

#     def create(self, validated_data):
#         request = self.context.get("request")
#         items_data = validated_data.pop("items")
#         address = validated_data.pop("address")
#         latitude = validated_data.pop("latitude")
#         longitude = validated_data.pop("longitude")
#         coupon = validated_data.pop("coupon", None)
#         branch = validated_data.pop("branch")
#         userid = validated_data.pop("userid")

#         # Verify user exists
#         try:
#             user = LoginTable.objects.get(id=userid, is_active=True)
#             print(f"User verified: ID={user.id}, Username={user.username}")
#         except ObjectDoesNotExist:
#             print(f"User verification failed: ID={userid} does not exist or is inactive")
#             raise serializers.ValidationError(f"User with id {userid} does not exist or is inactive.")

#         # Verify branch exists
#         try:
#             branch_instance = BranchTable.objects.get(id=branch.id)
#             print(f"Branch verified: ID={branch_instance.id}, Name={branch_instance.name}")
#         except ObjectDoesNotExist:
#             print(f"Branch verification failed: ID={branch.id} does not exist")
#             raise serializers.ValidationError(f"Branch with id {branch.id} does not exist.")

#         # Prepare address data
#         address_data = {
#             'address': address,
#             'latitude': latitude,
#             'longitude': longitude,
#             'city': validated_data.get('city', 'Kozhikode'),
#             'state': validated_data.get('state', 'Kerala'),
#             'postal_code': validated_data.get('postal_code', '673004'),
#             'country': validated_data.get('country', 'India'),
#             'name': validated_data.get('name', user.username),
#             'phone': validated_data.get('phone', user.phone or '')
#         }

#         # Check if address already exists
#         try:
#             address_instance = AddressTable.objects.filter(
#                 userid_id=userid,
#                 address=address_data['address']
#             ).first()
#             if not address_instance:
#                 address_instance = AddressTable.objects.create(
#                     userid=user,
#                     **address_data
#                 )
#                 print(f"Created new address: ID={address_instance.id}, Address={address_instance.address}")
#             else:
#                 print(f"Reused existing address: ID={address_instance.id}, Address={address_instance.address}")
#         except Exception as e:
#             print(f"Address creation failed: {str(e)}")
#             raise serializers.ValidationError(f"Failed to create or retrieve address: {str(e)}")

#         # Create order
#         try:
#             order = OrderTable.objects.create(
#                 userid=user,
#                 branch=branch_instance,
#                 address=address_instance,
#                 coupon=coupon,
#                 latitude=latitude,
#                 longitude=longitude,
#                 payment_method=validated_data.get('payment_method'),
#                 delivery_instructions=validated_data.get('delivery_instructions', ''),
#                 phone_number=address_data['phone']
#             )
#             print(f"Created order: ID={order.id}, UserID={order.userid_id}, Branch={order.branch_id}, Address={order.address_id}, Coupon={order.coupon_id}")
#         except Exception as e:
#             print(f"Order creation failed: {str(e)}")
#             raise serializers.ValidationError(f"Failed to create order: {str(e)}")

#         # Create order items
#         try:
#             for item_data in items_data:
#                 # item = ItemTable.objects.get(id=item_data['itemname'])
#                 item = item_data['itemname']
#                 order_item = OrderItemTable.objects.create(
#                     order=order,
#                     itemname=item,
#                     price=item_data['price'],
#                     quantity=str(item_data['quantity']),
#                     variant_id=item_data.get('variant_id'),
#                     instruction=item_data.get('instruction', ''),
#                     addon_id=item_data.get('addon_id')
#                 )
#                 print(f"Created order item: ItemID={order_item.itemname_id}, Quantity={order_item.quantity}, Price={order_item.price}")
#         except Exception as e:
#             print(f"Order item creation failed: {str(e)}")
#             raise serializers.ValidationError(f"Failed to create order item: {str(e)}")
#         return order

import base64
import decimal
    
import io
import base64
from django.core.files.base import ContentFile
from pydub import AudioSegment
import os
from django.core.files.uploadedfile import InMemoryUploadedFile

class UserOrderSerializer(serializers.ModelSerializer):
    items = UserOrderItemSerializer(many=True)
    branchid = serializers.PrimaryKeyRelatedField(source="branch", queryset=BranchTable.objects.all())
    coupon_code = serializers.PrimaryKeyRelatedField(source="coupon", queryset=CouponTable.objects.all(), required=False, allow_null=True)

    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    discount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    grand_total = serializers.DecimalField(source="totalamount", max_digits=10, decimal_places=2)

    # Audio file
    audio = serializers.FileField(
        source="voice_instruction",
        required=False,
        allow_null=True,
        use_url=True
    )

    userid = serializers.IntegerField(write_only=True)
    address = serializers.CharField(write_only=True)
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)

    class Meta:
        model = OrderTable
        fields = [
            'latitude', 'longitude', 'address', 'items',
            'payment_method', 'coupon_code', 'branchid',
            'delivery_instructions', 'cooking_instructions',
            'audio', 'userid', 'subtotal', 'discount', 'grand_total'
        ]

    def validate(self, data):
        if not data.get("items"):
            raise serializers.ValidationError("At least one item is required.")

        userid = data.get("userid")
        if not ProfileTable.objects.filter(loginid_id=userid).exists():
            raise serializers.ValidationError(f"Profile for user id {userid} does not exist.")

        return data

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        address = validated_data.pop("address")
        latitude = validated_data.pop("latitude")
        longitude = validated_data.pop("longitude")
        userid = validated_data.pop("userid")

        # ✅ Profile lookup
        try:
            profile = ProfileTable.objects.get(loginid_id=userid)
            user = profile.loginid
        except ProfileTable.DoesNotExist:
            raise serializers.ValidationError(f"Profile for user id {userid} does not exist.")

        # ✅ Address save/update
        address_instance, _ = AddressTable.objects.update_or_create(
            userid=user,
            address=address,
            defaults={
                "latitude": latitude,
                "longitude": longitude,
                "city": "Kozhikode",
                "state": "Kerala",
                "postal_code": "673004",
                "country": "India",
                "name": user.username,
                "phone": user.phone or ""
            }
        )

        # ✅ Totals
        subtotal = decimal.Decimal(validated_data.pop("subtotal", 0))
        discount = decimal.Decimal(validated_data.pop("discount", 0))
        totalamount = decimal.Decimal(validated_data.pop("totalamount", 0))

        # ✅ Create order
        order = OrderTable.objects.create(
            userid=profile,
            address=address_instance,
            subtotal=subtotal,
            discount=discount,
            totalamount=totalamount,
            latitude=latitude,
            longitude=longitude,
            phone_number=address_instance.phone,
            **validated_data
        )

        # ✅ Audio conversion (AAC → MP3, trim 30s)
        audio_data = validated_data.pop("voice_instruction", None)
        if audio_data:
            try:
                audio_file = audio_data.file
                audio_segment = AudioSegment.from_file(audio_file, format="aac")
                trimmed_audio = audio_segment[:30 * 1000]

                mp3_io = io.BytesIO()
                trimmed_audio.export(mp3_io, format="mp3")
                mp3_io.seek(0)

                mp3_file = InMemoryUploadedFile(
                    mp3_io,
                    None,
                    f"voice_instruction_{order.id}.mp3",
                    'audio/mpeg',
                    mp3_io.getbuffer().nbytes,
                    None
                )
                order.voice_instruction.save(f"voice_instruction_{order.id}.mp3", mp3_file)
                order.save()
            except Exception as e:
                print(f"Audio conversion failed: {e}")

        # ✅ Save order items
        for item_data in items_data:
            OrderItemTable.objects.create(
                order=order,
                itemname=item_data["itemname"],
                price=item_data["price"],
                quantity=str(item_data["quantity"]),
                variant_id=item_data.get("variant"),
                instruction=item_data.get("instruction", ""),
                addon_id=item_data.get("addon_id")
            )

        return order



    
class OrderHistorySerializer(serializers.ModelSerializer):
    items = OrderItemTableSerializer(many=True, source='orderitemtable_set', read_only=True)
    address = AddressTableSerializer(read_only=True)
    delivery = DeliveryTableSerializer(read_only=True)

    class Meta:
        model = OrderTable
        fields = [
            'id',
            'userid',
            'address',
            'delivery',
            'total_amount',
            'status',
            'payment_method',
            'created_at',
            'updated_at',
            'items',
        ]


    
    
class OrderItemRetrieveSerializer(serializers.ModelSerializer):
    itemname = serializers.StringRelatedField()
    variant = serializers.StringRelatedField()
    addon = serializers.StringRelatedField()

    class Meta:
        model = OrderItemTable
        fields = ['id', 'itemname', 'quantity', 'price', 'instruction', 'variant', 'addon']

class OrderRetrieveSerializer(serializers.ModelSerializer):
    userid = serializers.StringRelatedField(source='userid.name')
    branch = serializers.StringRelatedField()
    coupon = serializers.StringRelatedField()
    address = serializers.StringRelatedField()
    deliveryid = serializers.StringRelatedField() 
    order_item = OrderItemRetrieveSerializer(many=True, read_only=True) 
 
    class Meta:
        model = OrderTable
        fields = [
            'id', 'userid', 'branch', 'coupon', 'address', 'deliveryid', 'subtotal',
            'tax', 'discount', 'totalamount', 'latitude', 'longitude', 'paymentstatus',
            'orderstatus', 'cooking_instructions', 'delivery_instructions',
            'payment_method', 'phone_number', 'created_at', 'updated_at', 'order_item'
        ] 



class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingTable
        fields = ['userid', 'itemid', 'rating_type', 'rating', 'comment']
        read_only_fields = []  
        extra_kwargs = {
            'rating_type': {'required': True},
            'rating': {'required': True},
            'comment': {'required': False, 'allow_blank': True}
        }

    def validate(self, data):
        rating_type = data.get('rating_type')
        if rating_type not in ['SERVICE', 'DISH']:
            raise serializers.ValidationError({
                'rating_type': 'Invalid rating type. Must be SERVICE or DISH.'
            })

        rating = str(data.get('rating', '')).strip() 

        if rating_type == 'SERVICE':
            valid_ratings = ['1', '2', '3', '4', '5', 'Good', 'Not Good']
            if rating not in valid_ratings:
                raise serializers.ValidationError({
                    'rating': 'Invalid rating for SERVICE. Must be 1-5 or Good/Not Good.'
                })

        data['rating'] = rating
        return data