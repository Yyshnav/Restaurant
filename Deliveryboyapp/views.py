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
from sympy import Q

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
from django.contrib.auth.hashers import make_password


# from Accountapp.serializer import ChatMessageSerializer
from .fcm_utils import send_fcm_notification


# class SendTestNotification(APIView):
#     permission_classes = [AllowAny]

#     permission_classes = [AllowAny]

#     def post(self, request):
#         fcm_token = request.data.get('fcm_token',)
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

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# @method_decorator(csrf_exempt, name='dispatch')
# class DeliveryBoyLoginAPIView(APIView):
#     permission_classes = [AllowAny]
#     def post(self, request):
#         print(request.data)
#         username = request.data.get('username')
#         password = request.data.get('password')
#         user = authenticate(username=username, password=password)

#         if user is not None:
#             # Check if user has 'DELIVERY' role
#             if user.user_roles.filter(role='DELIVERY').exists():
               
#                 if hasattr(user, 'deliveryboy_profile'):  # Assuming profile is set up
#                     # token, created = Token.objects.get_or_create(user=user)
#                     refresh = RefreshToken.for_user(user)
#                     return Response({
#                         'token': str(refresh.access_token),
#                         'refresh': str(refresh),
#                         # 'token': token.key
#                     }, status=status.HTTP_200_OK) 
#                 else:
#                     return Response({'error': 'Not a delivery boy'}, status=status.HTTP_403_FORBIDDEN)
#             else:
#                 return Response({'error': 'User does not have DELIVERY role'}, status=status.HTTP_403_FORBIDDEN)
        
#         return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@method_decorator(csrf_exempt, name='dispatch')
class DeliveryBoyLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(request.data)
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check role and profile
        if not user.user_roles.filter(role='DELIVERY').exists():
            return Response({'error': 'User does not have DELIVERY role'}, status=status.HTTP_403_FORBIDDEN)

        if not hasattr(user, 'deliveryboy_profile'):
            return Response({'error': 'Not a delivery boy'}, status=status.HTTP_403_FORBIDDEN)

        # Generate JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'roles': [r.role for r in user.user_roles.all()]
            }
        }, status=status.HTTP_200_OK)
# Assuming you have an Order model with a foreign key to the delivery boy user

class LatestPendingOrdersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user 
        # Ensure user has DELIVERY role
        
        if not user.user_roles.filter(role='DELIVERY').exists():
            return Response({'error': 'User does not have DELIVERY role'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Get the DeliveryBoyTable object for this user
            delivery_boy = DeliveryBoyTable.objects.get(userid=user)
        except DeliveryBoyTable.DoesNotExist:
            return Response({'error': 'DeliveryBoyTable not found for user'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get latest orders assigned to this delivery boy with status 'PENDING'
        orders = OrderTable.objects.filter(deliveryid=delivery_boy, orderstatus__in=['PENDING', 'ACCEPTED', 'ASSIGNED']).order_by('-id')
        serializer = OrderSerializer(orders, many=True)
        print("DeliveryBoy:", delivery_boy.id)
        print("Orders count:", orders.count())
        print("All Orders for this delivery boy:", list(
            OrderTable.objects.filter(deliveryid=delivery_boy).values('id','orderstatus')
        ))
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

    def post(self, request, order_id):
        print(f"------------------- Update Order Request for ID {order_id} -------------------")
        user = request.user.id

        # Validate delivery boy profile
        try:
            delivery_boy = DeliveryBoyTable.objects.get(userid=user)
            print(f"✅ Delivery Boy Found: {delivery_boy}")
        except DeliveryBoyTable.DoesNotExist:
            print("❌ Delivery Boy Profile Not Found")
            return Response({'error': 'Delivery boy profile not found'}, status=status.HTTP_404_NOT_FOUND)

        # Validate input
        serializer = InputSerializer(data=request.data)
        if not serializer.is_valid():
            print("❌ Serializer Validation Failed:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        print(f"✅ Validated Data: {data}")

        if data['order_id'] != order_id:
            print(f"❌ Order ID Mismatch: URL={order_id}, Body={data['order_id']}")
            return Response({'error': 'Order ID mismatch'}, status=status.HTTP_400_BAD_REQUEST)

        # Get order
        try:
            order = OrderTable.objects.get(id=order_id, deliveryid=delivery_boy)
            print(f"✅ Order Found: {order}")
        except OrderTable.DoesNotExist:
            print("❌ Order not found or not assigned to this delivery boy")
            return Response({'error': 'Order not found or not assigned to you'}, status=status.HTTP_404_NOT_FOUND)

        # Update order status and payment details
        new_status = data['status']
        payment_done = data.get('paymentDone', False)
        payment_type = data.get('paymentType')

        order.orderstatus = new_status
        if payment_done and payment_type:
            order.paymentstatus = 'PAID'
            order.payment_method = payment_type
        elif payment_done:
            print("❌ Payment type required when payment is done")
            return Response({'error': 'Payment type is required when payment is done'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            order.paymentstatus = 'PENDING'
            order.payment_method = 'PENDING'

        order.save()
        print(f"✅ Order Updated: status={order.orderstatus}, paymentstatus={order.paymentstatus}")

        # ------------------------------
        # 🔔 Send Notification to User
        # ------------------------------
        try:
            user_login = order.userid.loginid  # Profile → LoginTable
            user_token = getattr(user_login, "notification_token", None)
            print(f"📱 User Login: {user_login}, Token: {user_token}")

            if user_token:
                if new_status == 'PICKED':
                    title = "Order Picked 🚚"
                    body = f"Your order #{order.id} has been picked up by {delivery_boy.name}."
                elif new_status == 'DELIVERED':
                    title = "Order Delivered 🎉"
                    body = f"Your order #{order.id} has been successfully delivered."
                elif new_status == 'ACCEPTED':
                    title = "Order Accepted ✅"
                    body = f"Your order #{order.id} has been accepted and will be prepared soon."
                elif new_status == 'ASSIGNED':
                    title = "Order Assigned 👨‍🍳"
                    body = f"Your order #{order.id} has been assigned to {delivery_boy.name}."
                else:
                    title = "Order Update 📦"
                    body = f"Your order #{order.id} status has been updated to {new_status}."

                send_fcm_notification(
                    token=user_token,
                    title=title,
                    body=body,
                    project="user"
                )
                print(f"✅ Notification Sent: {title}")
            else:
                print("⚠️ No notification token found for user.")
        except Exception as e:
            print(f"❌ Error Sending Notification: {e}")

        # Return updated order
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_200_OK)

    

class OrderDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        user = request.user
        # Ensure user has DELIVERY role
        if not user.user_roles.filter(role='DELIVERY').exists():
            return Response({'error': 'User does not have DELIVERY role'}, status=status.HTTP_403_FORBIDDEN)
        try:
            delivery_boy = DeliveryBoyTable.objects.get(userid=user)
        except DeliveryBoyTable.DoesNotExist:
            return Response({'error': 'Delivery boy profile not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            order = OrderTable.objects.get(id=order_id, deliveryid=delivery_boy)
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
    authentication_classes = [JWTAuthentication]
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
        try:
            delivery_boy = DeliveryBoyTable.objects.get(userid=user)
            print(f"Delivery Boy: {delivery_boy}")
        except DeliveryBoyTable.DoesNotExist:
            return Response({'error': 'Delivery boy profile not found'}, status=status.HTTP_404_NOT_FOUND)
        # Ensure user has DELIVERY role
        if not user.user_roles.filter(role='DELIVERY').exists():
            return Response({'error': 'User does not have DELIVERY role'}, status=status.HTTP_403_FORBIDDEN)
        # Fetch orders assigned to this delivery boy that are not 'PENDING'
        orders = OrderTable.objects.filter(deliveryid=delivery_boy).exclude(orderstatus='PENDING').order_by('-id')
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
        print(f"Generated OTP for {email}: {otp}")
        OTP_STORE[email] = {'otp': otp, 'expires': datetime.now() + timedelta(minutes=5)}
        send_mail(
            'Your OTP for Password Reset',
            f'Your OTP is: {otp} valid for 5 minutes.',

            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
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
            return Response({'message': 'Invalid OTP','success':False}, status=status.HTTP_400_BAD_REQUEST)
        if datetime.now() > otp_data['expires']:
            return Response({'message': 'OTP expired','success':False}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'OTP verified','success':True}, status=status.HTTP_200_OK)

class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        print(request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data['email']
       
        new_password = serializer.validated_data['new_password']
       
        try:
            user = DeliveryBoyTable.objects.get(email=email)
        except DeliveryBoyTable.DoesNotExist:
            return Response({'message': 'User not found','status':False}, status=status.HTTP_404_NOT_FOUND)
        user.password = make_password(new_password)
        user.save()
        OTP_STORE.pop(email, None)
        return Response({'message': 'Password reset successful','status':True}, status=status.HTTP_200_OK)

class ChatHistoryAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        print('order_id:', order_id)
        try:
            chats = ChatMessage.objects.filter(order=order_id).order_by('timestamp')
            serializer = ChatMessageSerializer(chats, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SubmitFeedbackAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user.id
        print(f"User ID: {user}, Request Data: {request.data}")
        try:
            delivery_boy = DeliveryBoyTable.objects.get(userid=user)
            print(f"Delivery Boy: {delivery_boy}")
        except DeliveryBoyTable.DoesNotExist:
            return Response({'error': 'Delivery boy profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserFeedbackSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order_id = serializer.validated_data['order_id']
        rating = serializer.validated_data['rating']
        feedback = serializer.validated_data.get('feedback')

        try:
            order = OrderTable.objects.get(id=order_id, deliveryid=delivery_boy)
        except OrderTable.DoesNotExist:
            return Response({'error': 'Order not found or not assigned to you'}, status=status.HTTP_404_NOT_FOUND)

        # Save feedback to FeedbackTable (assumed model)
        UserFeedbackTable.objects.create(
            order=order,
            delivery_boy=delivery_boy,
            rating=rating,
            feedback=feedback
        )
        print(f"Feedback saved: Order {order_id}, Rating {rating}, Feedback {feedback}")
        return Response({'success': 'Feedback submitted successfully'}, status=status.HTTP_201_CREATED)
    
class UpdateDeliveryBoyLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get the authenticated delivery boy
            delivery_boy = DeliveryBoyTable.objects.get(userid=request.user)
            
            # Validate request data using serializer
            serializer = DeliveryBoyLocationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Extract validated data
            validated_data = serializer.validated_data

            # Update or create the location
            location, created = DeliveryBoyLocation.objects.update_or_create(
                delivery_boy=delivery_boy,
                defaults={
                    'latitude': validated_data['latitude'],
                    'longitude': validated_data['longitude']
                }
            )

            return Response(
                {
                    "message": "Location updated successfully",
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "updated_at": location.updated_at
                },
                status=status.HTTP_200_OK
            )

        except DeliveryBoyTable.DoesNotExist:
            print(f"Delivery boy not found for user: {request.user}")
            return Response(
                {"error": "Delivery boy not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error updating location: {e}")
            return Response(
                {"error": f"Failed to update location: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )