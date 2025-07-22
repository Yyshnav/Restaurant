from rest_framework import serializers
from django.contrib.auth import get_user_model

from Accountapp.models import AddressTable, CartTable, DeliveryTable, FeedbackTable, ItemTable, OrderItemTable, OrderTable, ProfileTable, RatingTable, WishlistTable
from Accountapp.serializer import LoginTableSerializer
from Adminapp.serializer import AddonSerializer, ItemSerializer, OrderTableSerializer
from Adminapp.serializer import AddonSerializer, ItemSerializer, OrderTableSerializer

LoginTable = get_user_model()

class ProfileTableSerializer(serializers.ModelSerializer):
    loginid = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ProfileTable
        fields = [
            'id', 'name', 'phone', 'image', 'email', 'dob',
            'loginid',
            'created_at', 'updated_at'
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
# class RatingTableSerializer(serializers.ModelSerializer):
#     # Read-only nested fields
#     userid = ProfileTableSerializer(read_only=True)
#     itemid = ItemSerializer(read_only=True)

#     # Write-only fields for creation/updating
#     userid_id = serializers.PrimaryKeyRelatedField(
#         queryset=LoginTable.objects.all(), write_only=True, source='userid'
#     )
#     itemid_id = serializers.PrimaryKeyRelatedField(
#         queryset=ItemTable.objects.all(), write_only=True, source='itemid', allow_null=True, required=False
#     )

#     class Meta:
#         model = RatingTable
#         fields = [
#             'id',
#             'userid',       
#             'userid_id',     
#             'itemid',       
#             'itemid_id',     
#             'rating_type',
#             'rating',
#             'comment',
#             'createdat',
#             'updatedat',
#         ]

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

# class WishlistSerializer(serializers.ModelSerializer):
#     # fooditem_name = serializers.CharField(source='fooditem.name', read_only=True)
#     # fooditem_image = serializers.CharField(source='fooditem.image_url', read_only=True)
#     # fooditem_price = serializers.DecimalField(source='fooditem.price', read_only=True, max_digits=10, decimal_places=2)
#     fooditem_details = ItemSerializer(many= True, read_only=True)
#     fooditem_id = serializers.PrimaryKeyRelatedField(
#         queryset=ItemTable.objects.all(), source='fooditem', write_only=True)

#     class Meta:
#         model = WishlistTable
#         fields = ['id', 'fooditem', 'fooditem_details', 'fooditem_id', 'added_at']
#         read_only_fields = ['id', 'added_at']
        # fields = ['id', 'fooditem', 'fooditem_name', 'fooditem_image', 'fooditem_price', 'added_at']
        # read_only_fields = ['id', 'added_at', 'fooditem_name', 'fooditem_image', 'fooditem_price']   

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

    class Meta:
        model = OrderItemTable
        # fields = ['id', 'order', 'itemname', 'quantity', 'price', 'instruction', 'addon']
        fields = '__all__'
        # fields = ['id', 'order', 'itemname', 'quantity', 'price', 'instruction', 'addon']
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

    class Meta:
        model = CartTable
        fields = [
            'id', 'fooditem', 'fooditem_name', 'quantity', 'price', 'addon', 'addon_name','fooditem_price',
            'instruction', 'added_at', 'updated_at', 'total_price'
        ]
        read_only_fields = ['id', 'added_at', 'updated_at', 'fooditem_name', 'addon_name']

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