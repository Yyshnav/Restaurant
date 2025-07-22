from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from Deliveryboyapp.serializer import *
from Accountapp.models import *
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import RefreshToken

# from Accountapp.models import UserRole  # Ensure this model exists and is related properly

# notification

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.http import HttpResponse


from Accountapp.serializer import ChatMessageSerializer
from .fcm_utils import send_fcm_notification


# class SendTestNotification(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         fcm_token = request.data.get('fcm_token',)
#         title = request.data.get('title', 'Test Notification')
#         body = request.data.get('body', 'This is a test message')

#         if not fcm_token:
#             return Response({"error": "FCM token is required"}, status=status.HTTP_400_BAD_REQUEST)

#         result = send_fcm_notification(fcm_token, title, body)
#         return Response(result, status=result['status_code'])
def send_notification_view(request):
    users = LoginTable.objects.filter(notification_token__isnull=False).exclude(notification_token='')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        title = request.POST.get('title', 'Hello')
        body = request.POST.get('body', 'This is a test')

        try:
            user = LoginTable.objects.get(id=user_id)
            fcm_token = user.notification_token

            if not fcm_token:
                return HttpResponse("Selected user has no FCM token.")

            result = send_fcm_notification(fcm_token, title, body)
            return HttpResponse(f"Notification sent. Response: {result}")

        except LoginTable.DoesNotExist:
            return HttpResponse("Invalid user selected.")

    return render(request, 'send_notification.html', {'users': users})
# import json
# import requests
# from google.oauth2 import service_account
# from google.auth.transport.requests import Request

# # Path to your Firebase service account JSON key


# def get_access_token():
#     credentials = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE,
#         scopes=["https://www.googleapis.com/auth/firebase.messaging"]
#     )
#     credentials.refresh(Request())
#     return credentials.token

# def send_fcm_notification(token, title, body):
#     access_token = get_access_token()

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json; UTF-8",
#     }

#     message = {
#         "message": {
#             "token": token,
#             "notification": {
#                 "title": title,
#                 "body": body
#             }
#         }
#     }

    
#     url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

#     response = requests.post(url, headers=headers, data=json.dumps(message))
#     return response.json()


class DeliveryBoyLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            # Check if user has 'DELIVERY' role
            if user.user_roles.filter(role='DELIVERY').exists():
                print('55555555555555555555555555555555555555555')
                if hasattr(user, 'deliveryboy_profile'):  # Assuming profile is set up
                    # token, created = Token.objects.get_or_create(user=user)
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'token': str(refresh.access_token),
                        'refresh': str(refresh),
                        # 'token': token.key
                    }, status=status.HTTP_200_OK) 
                else:
                    return Response({'error': 'Not a delivery boy'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'User does not have DELIVERY role'}, status=status.HTTP_403_FORBIDDEN)
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


# Assuming you have an Order model with a foreign key to the delivery boy user

class LatestPendingOrdersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    

    def get(self, request):
        user = request.user
        # Ensure user has DELIVERY role
        
        if not user.user_roles.filter(role='DELIVERY').exists():
            return Response({'error': 'User does not have DELIVERY role'}, status=status.HTTP_403_FORBIDDEN)
        # Get latest orders assigned to this delivery boy with status 'PENDING'
        orders = OrderTable.objects.filter(deliveryid=user, orderstatus='PENDING').order_by('-id')
        serializer = OrderSerializer(orders, many=True)
        print("Orders:", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)



class AssignedOrdersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Check if user has DELIVERY role
        if not user.user_roles.filter(role='DELIVERY').exists():
            return Response({'error': 'User does not have DELIVERY role'}, status=status.HTTP_403_FORBIDDEN)
        # Assuming Order has a field like 'assigned_to' pointing to the delivery boy user
        orders = OrderTable .objects.filter(deliveryid=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UpdateOrderStatusAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    

    def post(self, request):
        serializer = InputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order_id = serializer.validated_data['order_id']
        new_status = serializer.validated_data['status']

        try:
            order = OrderTable.objects.get(id=order_id, deliveryid=request.user)
        except OrderTable.DoesNotExist:
            return Response({'error': 'Order not found or not assigned to you'}, status=status.HTTP_404_NOT_FOUND)

        order.orderstatus = new_status
        order.save()
        return Response({'success': f'Order status updated to {new_status}'}, status=status.HTTP_200_OK)
    

class OrderDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        user = request.user
        # Ensure user has DELIVERY role
        if not user.user_roles.filter(role='DELIVERY').exists():
            return Response({'error': 'User does not have DELIVERY role'}, status=status.HTTP_403_FORBIDDEN)
        try:
            order = OrderTable.objects.get(id=order_id, deliveryid=user)
        except OrderTable.DoesNotExist:
            return Response({'error': 'Order not found or not assigned to you'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #profile section..........

class DeliveryBoyProfileAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

     # Adjust fields as per your model

    def get(self, request):
        print('rcvefv dg ')
        user = request.user
        try:
            profile = DeliveryBoyTable.objects.get(userid=user)
        except DeliveryBoyTable.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        try:
            profile = DeliveryBoyTable.objects.get(userid=user)
        except DeliveryBoyTable.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ChangePasswordAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)
    
   
class PostComplaintAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = request.user
        try:
            delivery_profile = DeliveryBoyTable.objects.get(user=user)
        except DeliveryBoyTable.DoesNotExist:
            return Response({'error': 'Delivery profile not found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        data['userid'] = user.id
        data['deliveryid'] = delivery_profile.id
        serializer = ComplaintSerializer(data=data)
        if serializer.is_valid():
            serializer.save(userid=user, deliveryid=delivery_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class OrderHistoryAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Ensure user has DELIVERY role
        if not user.user_roles.filter(role='DELIVERY').exists():
            return Response({'error': 'User does not have DELIVERY role'}, status=status.HTTP_403_FORBIDDEN)
        # Fetch orders assigned to this delivery boy that are not 'PENDING'
        orders = OrderTable.objects.filter(deliveryid=user).exclude(orderstatus='PENDING').order_by('-id')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    

class FeedbackAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data.copy()
        data['userid'] = user.id
        serializer = FeedbackSerializer(data=data)
        if serializer.is_valid():
            serializer.save(userid=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = request.user
        feedbacks = FeedbackTable.objects.filter(userid=user).order_by('-created_at')
        serializer = FeedbackSerializer(feedbacks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



#forgot password.......

# Simple in-memory OTP store (for demonstration; use a model for production)
OTP_STORE = {}

class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data['email']
        try:
            user = DeliveryBoyTable.objects.get(email=email)
        except DeliveryBoyTable.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        otp = get_random_string(length=4, allowed_chars='0123456789')
        OTP_STORE[email] = {'otp': otp, 'expires': datetime.now() + timedelta(minutes=10)}
        send_mail(
            'Your OTP for Password Reset',
            f'Your OTP is: {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True,
        )
        return Response({'success': 'OTP sent to your email'}, status=status.HTTP_200_OK)

class VerifyOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        otp_data = OTP_STORE.get(email)
        if not otp_data or otp_data['otp'] != otp:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        if datetime.now() > otp_data['expires']:
            return Response({'error': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': 'OTP verified'}, status=status.HTTP_200_OK)

class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']
        otp_data = OTP_STORE.get(email)
        if not otp_data or otp_data['otp'] != otp:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        if datetime.now() > otp_data['expires']:
            return Response({'error': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = DeliveryBoyTable.objects.get(email=email)
        except DeliveryBoyTable.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user.set_password(new_password)
        user.save()
        OTP_STORE.pop(email, None)
        return Response({'success': 'Password reset successful'}, status=status.HTTP_200_OK)
    


# class LogoutAPIView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         try:
#             # request.user.auth_token.delete()

#         except Exception:
#             return Response({'error': 'Logout failed'}, status=status.HTTP_400_BAD_REQUEST)
#         return Response({'success': 'Logged out successfully'}, status=status.HTTP_200_OK)


class ChatMessageAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            chats = ChatMessageTable.objects.filter(order_id=order_id)
            serializer = ChatMessageSerializer(chats, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, order_id):
        try:
            order = OrderTable.objects.get(id=order_id)

            sender_type = request.data.get('sender_type')  # "USER" or "DELIVERYBOY"
            message = request.data.get('message')

            if not message or not sender_type:
                return Response({'error': 'sender_type and message required'}, status=status.HTTP_400_BAD_REQUEST)

            if sender_type == 'USER':
                user = request.user
                delivery_boy = order.delivery_boy
            elif sender_type == 'DELIVERYBOY':
                delivery_boy = request.user.deliveryboy  # assuming OneToOne relationship
                user = order.user
            else:
                return Response({'error': 'Invalid sender_type'}, status=status.HTTP_400_BAD_REQUEST)

            chat = ChatMessageTable.objects.create(
                order=order,
                user=user,
                delivery_boy=delivery_boy,
                sender_type=sender_type,
                message=message
            )

            serializer = ChatMessageSerializer(chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except OrderTable.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


