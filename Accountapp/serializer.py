from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from Accountapp.models import ChatMessageTable, UserRole

LoginTable = get_user_model()

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', 'role']


class LoginTableSerializer(serializers.ModelSerializer):
    user_roles = UserRoleSerializer(many=True, read_only=True)
    class Meta:
        model = LoginTable
        fields = ['id', 'phone', 'user_roles', 'created_at', 'is_active']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginTable
        fields = ['phone', 'user_type']

    def create(self, validated_data):
        user_type = validated_data.get('user_type', 'USER')
        phone = validated_data.get('phone')

        user, created = LoginTable.objects.get_or_create(phone=phone, defaults={
            'user_type': user_type,
            'username': phone
        })

        if not created:
            # if user exists, we just update user_type in case it's different
            user.user_type = user_type
            user.save()

        return user


class PhoneOTPLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        phone = data.get("phone")
        otp = data.get("otp")

        try:
            user = LoginTable.objects.get(phone=phone)
        except LoginTable.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        if user.otp != otp:
            raise serializers.ValidationError("Invalid OTP")

        if not user.is_active:
            raise serializers.ValidationError("User is inactive")

        # Optional: reset OTP after login
        user.otp = None
        user.save()

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': LoginTableSerializer(user).data
        }
    
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessageTable
        fields = '__all__'

    