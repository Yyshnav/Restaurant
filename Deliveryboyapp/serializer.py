from rest_framework import serializers
from Accountapp import serializer
from Accountapp.models import *

class DeliveryBoyTableSerializer(serializers.ModelSerializer):
    userid = serializer.LoginTableSerializer(read_only=True)

    class Meta:
        model = DeliveryBoyTable
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTable
        fields = '__all__'

class InputSerializer(serializers.Serializer):
        order_id = serializers.IntegerField()
        status = serializers.ChoiceField(choices=['OUT_FOR_DELIVERY', 'DELIVERED'])

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
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6)
