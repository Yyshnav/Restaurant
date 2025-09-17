from rest_framework import serializers
from Accountapp import serializer
from Accountapp.models import *
from Userapp.serializer import ProfileTableSerializer,OrderItemTableSerializer,DeliveryTableSerializer,AddressTableSerializer
from Adminapp.serializer import AddonSerializer, BranchTableSerializer, ItemSerializer, ItemVariantSerializer 

class DeliveryBoyLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryBoyLocation
        fields = ['latitude', 'longitude', 'updated_at']

class DeliveryBoyTableSerializer(serializers.ModelSerializer):
    userid = serializer.LoginTableSerializer(read_only=True)
    location = DeliveryBoyLocationSerializer(read_only=True)

    class Meta:
        model = DeliveryBoyTable
        fields = '__all__'


class OrderTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTable
        fields = '__all__'

class DeliveryOrderItemTableSerializer(serializers.ModelSerializer):
    itemname = serializers.SerializerMethodField()
    variant = serializers.SerializerMethodField()
    addon = serializers.SerializerMethodField()

    class Meta:
        model = OrderItemTable
        fields = ['id', 'itemname', 'quantity', 'price', 'instruction', 'variant', 'addon']

    def get_itemname(self, obj):
        return {'name': obj.itemname.name} if obj.itemname else {'name': 'Unknown Item'}

    def get_variant(self, obj):
        return {'name': obj.variant.variant_name} if obj.variant else None

    def get_addon(self, obj):
        return {'name': obj.addon.name} if obj.addon else None


# class OrderSerializer(serializers.ModelSerializer):
#     userid = serializers.SerializerMethodField()
#     branch = BranchTableSerializer(read_only=True)
#     address=AddressTableSerializer(read_only=True)
#     order_item = OrderTableSerializer(read_only=True, many=True)
#     delivery_details = serializers.SerializerMethodField()

#     class Meta:
#         model = OrderTable
#         fields = '__all__' 

#     def get_userid(self, obj):
#         try:
#             profile = obj.userid.profile.first()
#             return ProfileTableSerializer(profile).data if profile else None
#         except:
#             return None

#     def get_delivery_details(self, obj):
#         try:
#             print("Getting delivery for order:", obj.id)
#             delivery = DeliveryTable.objects.filter(order=obj).first()
#             print("Found delivery:", delivery)
#             return DeliveryTableSerializer(delivery).data if delivery else None
#         except Exception as e:
#             print("Error getting delivery:", e)
#             return None

        
#     def get_address(self, obj):
#         try:
#             address = obj.address
#             return AddressTableSerializer(address).data if address else None
#         except:
#             return None


class OrderSerializer(serializers.ModelSerializer):
    userid = serializers.SerializerMethodField()
    branch = BranchTableSerializer(read_only=True)
    address = AddressTableSerializer(read_only=True)
    order_item = DeliveryOrderItemTableSerializer(many=True, read_only=True)
    delivery_details = serializers.SerializerMethodField()

    class Meta:
        model = OrderTable
        fields = '__all__'

    def get_userid(self, obj):
        try:
            if obj.userid:
                profile = obj.userid.loginid.first()
                return ProfileTableSerializer(profile).data if profile else {
                    'id': obj.userid.id,
                    'phone': obj.userid.phone or obj.phone_number or 'Unknown',
                    'user_roles': [{'id': role.id, 'role': role.role} for role in obj.userid.user_roles.all()]
                }
            return {
                'phone': obj.phone_number or 'Unknown',
                'user_roles': []
            }
        except Exception as e:
            # print(f"Error getting userid: {e}")
            return {
                'phone': obj.phone_number or 'Unknown',
                'user_roles': []
            }

    def get_delivery_details(self, obj):
        try:
            # print(f"Getting delivery for order: {obj.id}")
            delivery = DeliveryTable.objects.filter(order=obj).first()
            if delivery:
                return DeliveryTableSerializer(delivery).data
            return {
                'name': obj.phone_number or 'Unknown',
                'phone': obj.phone_number or '',
                'address': {
                    'address': obj.address.address if obj.address else 'Unknown Address',
                    'latitude': obj.latitude or 0.0,
                    'longitude': obj.longitude or 0.0
                },
                'instruction': obj.delivery_instructions or '',
                'voice_instruction': obj.voice_instruction.url if obj.voice_instruction else None
            }
        except Exception as e:
            print(f"Error getting delivery: {e}")
            return {
                'name': obj.phone_number or 'Unknown',
                'phone': obj.phone_number or '',
                'address': {
                    'address': obj.address.address if obj.address else 'Unknown Address',
                    'latitude': obj.latitude or 0.0,
                    'longitude': obj.longitude or 0.0
                },
                'instruction': obj.delivery_instructions or '',
                'voice_instruction': obj.voice_instruction.url if obj.voice_instruction else None
                
            }

    def get_address(self, obj):
        try:
            address = obj.address
            return AddressTableSerializer(address).data if address else None
        except Exception as e:
            print(f"Error getting address: {e}")
            return None


class InputSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=['ACCEPTED', 'DELIVERED'])
    payment_done = serializers.BooleanField(default=False, required=False)
    payment_type = serializers.ChoiceField(choices=['CASH', 'ONLINE'], required=False, allow_null=True)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryBoyTable
        fields = ['id', 'name', 'phone', 'address', 'email','image']

class ChangePasswordSerializer(serializers.Serializer):
        old_password = serializers.CharField(required=True)
        new_password = serializers.CharField(required=True, min_length=8)

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintTable
        fields = ['id', 'userid', 'deliveryid', 'complaint', 'image', 'reply', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reply', 'created_at', 'updated_at', 'userid', 'deliveryid']


class FeedbackSerializer(serializers.ModelSerializer):
        class Meta:
            model = FeedbackTable
            fields = ['id', 'userid', 'feedback', 'rating', 'created_at']
            read_only_fields = ['id', 'userid', 'created_at']

#forgot password

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    # otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6)

class OrderItemDetailSerializer(serializers.ModelSerializer):
    itemname = ItemSerializer()
    addon = serializers.SerializerMethodField()

    class Meta:
        model = OrderItemTable
        fields = ['id', 'itemname', 'price', 'quantity', 'instruction', 'addon']

    def get_addon(self, obj):
        addon_id = obj.addon_id
        if addon_id:
            try:
                addon = ItemTable.objects.get(id=addon_id)
                return AddonSerializer(addon).data
            except ItemTable.DoesNotExist:
                return None
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Inject selected variant into the itemname field
        try:
            variant = ItemVariantTable.objects.get(id=instance.variant_id)
            data['itemname']['variant'] = {
                "id": variant.id,
                "variant_name": variant.variant_name,
                "price": variant.price
            }
        except ItemVariantTable.DoesNotExist:
            data['itemname']['variant'] = None

        return data


class TrackOrderSerializer(serializers.ModelSerializer):
    delivery_details = DeliveryBoyTableSerializer(source='deliveryid', read_only=True)

    items = OrderItemDetailSerializer(source='order_item', many=True, read_only=True)

    username = serializers.CharField(source='userid.name', read_only=True)

    restaurant_details = BranchTableSerializer(source='branch', read_only=True)
    branch_id = serializers.IntegerField(source='branch.id', read_only=True)

    class Meta:
        model = OrderTable
        fields = [
            'id',
            'orderstatus',
            'paymentstatus',
            'subtotal',
            'tax',
            'discount',
            'totalamount',
            'latitude',
            'longitude',
            'phone_number',
            'username',
            'created_at',
            'updated_at',
            'delivery_details',
            # 'user_profile',
            'items',
            'restaurant_details',
            'branch_id'
        ]

class UserFeedbackSerializer(serializers.Serializer):
    order_id = serializers.CharField()
    rating = serializers.FloatField(min_value=1.0, max_value=5.0)
    feedback = serializers.CharField(max_length=500, allow_null=True, required=False)

class DeliveryBoyLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryBoyLocation
        fields = ['latitude', 'longitude']
        extra_kwargs = {
            'latitude': {'required': True},
            'longitude': {'required': True},
        }

    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees.")
        return value

    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees.")
        return value
    


from rest_framework import serializers

class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImageTable
        fields = ['id', 'image', 'uploaded_at']

class ItemVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemVariantTable
        fields = ['id', 'variant_name', 'price']

class VoiceDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceDescriptionTable
        fields = ['id', 'language', 'audio_file']

class AddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddonTable
        fields = ['id', 'name', 'quantity', 'description', 'image', 'price']

class ItemSerializer(serializers.ModelSerializer):
    images = ItemImageSerializer(many=True, read_only=True)
    variants = ItemVariantSerializer(many=True, read_only=True)
    voice_descriptions = VoiceDescriptionSerializer(many=True, read_only=True)
    addons = AddonSerializer(many=True, read_only=True)

    class Meta:
        model = ItemTable
        fields = [
            'id', 'name', 'category', 'subcategory', 'subsubcategory', 'is_veg',
            'description', 'price', 'preparation_time', 'inventory', 'calories',
            'fast_delivery', 'newest', 'available', 'created_at', 'updated_at',
            'images', 'variants', 'voice_descriptions', 'addons'
        ]

class OfferSerializer(serializers.ModelSerializer):
    itemid = ItemSerializer(read_only=True)

    class Meta:
        model = OfferTable
        fields = [
            'id', 'name', 'startdate', 'enddate', 'branch',
            'offer_percentage', 'itemid', 'offerdescription',
            'createdat', 'updatedat', 'is_active'
        ]

class CarouselSerializer(serializers.ModelSerializer):
    offer = OfferSerializer(read_only=True)

    class Meta:
        model = CarouselTable
        fields = [
            'id', 'image', 'offer', 'branch',
            'offer_percentage', 'startdate', 'enddate',
            'created_at', 'is_active'
        ]
