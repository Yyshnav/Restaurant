from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random
from Accountapp.models import ItemTable, LoginTable, WishlistTable
from django.conf import settings
from Restaurant.Userapp.serializer import ProfileTableSerializer
from twilio.rest import Client
from Accountapp.models import ProfileTable
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework.permissions import IsAuthenticated
import secrets
from rest_framework.permissions import AllowAny
from Userapp.serializer import ProfileTableSerializer, WishlistSerializer


# Create your views here.
#auth views

class SendOTPView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        if not phone:
            return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        otp = random.randint(100000, 999999)
        try:
            user, created = LoginTable.objects.get_or_create(phone=phone)
            user.otp = otp
            user.save()
        except Exception as e:
            return Response({'error': 'Database error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f'Your OTP is {otp}',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )
        except Exception as e:
            return Response({'error': 'Failed to send SMS.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)
    
class VerifyOTPView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        otp = request.data.get('otp')

        if not phone or not otp:
            return Response({'error': 'Phone and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = LoginTable.objects.get(phone=phone)

            if str(user.otp) == str(otp):
                # Optional: Update OTP verification timestamp or status
                user.otp_verified = True
                user.save()

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                return Response({
                    'message': 'OTP verified successfully.',
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        except LoginTable.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Database error.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
class ResendOTPView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        if not phone:
            return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = LoginTable.objects.get(phone=phone)
            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()
        except LoginTable.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'error': 'Database error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f'Your OTP is {otp}',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )
        except Exception:
            return Response({'error': 'Failed to send SMS.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'message': 'OTP resent successfully.'}, status=status.HTTP_200_OK)
class AddBasicDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Try to get or create the profile for the user
        profile, created = ProfileTable.objects.get_or_create(user=user)

        # Include `loginid` in the serializer data as it's a required field
        data = request.data.copy()
        data['loginid'] = user.id  # assuming LoginTable is linked to User model via OneToOne

        serializer = ProfileTableSerializer(profile, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Basic details added successfully.', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
# home views.........................................................

class HomeScreenDataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Example data, replace with actual queries/models as needed
        banners = [
            {"id": 1, "image_url": "https://example.com/banner1.jpg"},
            {"id": 2, "image_url": "https://example.com/banner2.jpg"},
        ]
        categories = [
            {"id": 1, "name": "Pizza"},
            {"id": 2, "name": "Burgers"},
            {"id": 3, "name": "Drinks"},
        ]
        spotlight = [
            {"id": 101, "image_url": "https://example.com/item1.jpg"},
            {"id": 102,  "image_url": "https://example.com/item2.jpg"},
        ]
        whats_new = [
            {"id": 101, "image_url": "https://example.com/item1.jpg"},
            {"id": 102,  "image_url": "https://example.com/item2.jpg"},
        ]
        return Response({
            'whats_new':whats_new,
            "banners": banners,
            "categories": categories,
            "spotlight": spotlight
        }, status=status.HTTP_200_OK)
    
class FeaturedItemsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Example featured items data, replace with actual queries/models as needed
        featured_items = [
            {"id": 201, "name": "Margherita Pizza", "image_url": "https://example.com/featured1.jpg"},
            {"id": 202, "name": "Cheese Burger", "image_url": "https://example.com/featured2.jpg"},
            {"id": 203, "name": "Mojito", "image_url": "https://example.com/featured3.jpg"},
        ]
        return Response({"featured_items": featured_items}, status=status.HTTP_200_OK)
    
# wish list views.........................................................



class AddToWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        fooditem_id = request.data.get('fooditem_id')
        if not fooditem_id:
            return Response({'error': 'fooditem_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            fooditem = ItemTable.objects.get(id=fooditem_id)
            wishlist_item, created = WishlistTable.objects.get_or_create(
                userid=request.user, fooditem=fooditem
            )
            if not created:
                return Response({'message': 'Item already in wishlist.'}, status=status.HTTP_200_OK)
            
            serializer = WishlistSerializer(wishlist_item)
            return Response({'message': 'Item added to wishlist.', 'item': serializer.data}, status=status.HTTP_201_CREATED)
        
        except ItemTable.DoesNotExist:
            return Response({'error': 'Food item does not exist.'}, status=status.HTTP_404_NOT_FOUND)


class RemoveFromWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, fooditem_id):
        try:
            wishlist_item = WishlistTable.objects.get(userid=request.user, fooditem_id=fooditem_id)
            wishlist_item.delete()
            return Response({'message': 'Item removed from wishlist.'}, status=status.HTTP_200_OK)
        except WishlistTable.DoesNotExist:
            return Response({'error': 'Item not found in wishlist.'}, status=status.HTTP_404_NOT_FOUND)


class WishlistItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wishlist_items = WishlistTable.objects.filter(userid=request.user).select_related('fooditem')
        serializer = WishlistSerializer(wishlist_items, many=True)
        return Response({'wishlist_items': serializer.data}, status=status.HTTP_200_OK)



    

 