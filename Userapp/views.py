from multiprocessing.connection import Client
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random
from Accountapp.models import CarouselTable, CartTable, ItemTable, LoginTable, SpotlightTable, UserRole, WishlistTable
from django.conf import settings
from Adminapp.serializer import CarouselSerializer, ItemSerializer, SpotlightSerializer
from Userapp.serializer import ProfileTableSerializer
# from twilio.rest import Client
from Accountapp.models import ProfileTable
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework.permissions import IsAuthenticated
import requests
import secrets
from rest_framework.permissions import AllowAny
from Userapp.serializer import CartSerializer, ProfileLocationUpdateSerializer, ProfileNameUpdateSerializer, ProfileTableSerializer, WishlistSerializer


# Create your views here.
#auth views

class SendOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        phone = request.data.get('phone')
        print(phone)
        if not phone:
            return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        otp = random.randint(1000, 9999)
        print(otp)
        try:
            user, created = LoginTable.objects.get_or_create(phone=phone)
            user.otp = otp
            user.save()
            #need to change later
            if created:
                # 🔒 Assign 'USER' role to new user
                user_role = UserRole.objects.get(role='USER')
                user.user_roles.add(user_role)
                user.save()
        except Exception as e:
            return Response({'error': 'Database error.'}, status=status.HTTP_201_CREATED)
        #need o chage later
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f'Your OTP is {otp}',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )
        except Exception as e:
            return Response({'error': 'Failed to send SMS.'}, status=status.HTTP_201_CREATED)
        
        return Response({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)

# class SendOTPView(APIView):
#     def post(self, request):
#         phone = request.data.get('phone')
#         if not phone:
#             return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Generate OTP
#         otp = random.randint(1000, 9999)

#         # Save or create user with OTP
#         try:
#             user, created = LoginTable.objects.get_or_create(phone=phone)
#             user.otp = otp
#             user.save()
#         except Exception as e:
#             return Response({'error': 'Database error.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         # Send OTP using Fast2SMS
#         try:
#             url = "https://www.fast2sms.com/dev/bulkV2"
#             headers = {
#                 'authorization': settings.FAST2SMS_API_KEY,
#                 'Content-Type': "application/json"
#             }
#             payload = {
#                 "route": "otp",
#                 "variables_values": str(otp),
#                 "numbers": phone.replace('+91', '')  # Fast2SMS expects 10-digit number
#             }

#             response = requests.post(url, json=payload, headers=headers)
#             if response.status_code != 200:
#                 return Response({
#                     'error': 'Failed to send OTP.',
#                     'details': response.text
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         except Exception as e:
#             return Response({'error': 'SMS sending failed.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response({'message': 'OTP sent successfully.', 'otp': otp}, status=status.HTTP_200_OK)  # `otp` can be hidden in production
    
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
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

                print(f"Access Token: {access_token}")
                print(f"Refresh Token: {refresh_token}")

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

# class ResendOTPView(APIView):
#     def post(self, request):
#         phone = request.data.get('phone')
#         if not phone:
#             return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = LoginTable.objects.get(phone=phone)
#             otp = random.randint(1000, 9999)
#             user.otp = otp
#             user.save()
#         except LoginTable.DoesNotExist:
#             return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception:
#             return Response({'error': 'Database error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         try:
#             url = "https://www.fast2sms.com/dev/bulkV2"
#             headers = {
#                 'authorization': settings.FAST2SMS_API_KEY,
#                 'Content-Type': "application/json"
#             }
#             payload = {
#                 "route": "otp",
#                 "variables_values": str(otp),
#                 "numbers": phone.replace('+91', '')  # Fast2SMS usually expects 10-digit number
#             }

#             response = requests.post(url, json=payload, headers=headers)

#             if response.status_code == 200:
#                 return Response({'message': 'OTP resent successfully.'}, status=status.HTTP_200_OK)
#             else:
#                 return Response({'error': 'Failed to send OTP.', 'details': response.text}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             return Response({'error': 'SMS sending failed.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        phone = request.data.get('phone')
        if not phone:
            return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = LoginTable.objects.get(phone=phone)
            otp = random.randint(1000, 9999)
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
        # print("🔥 View was called")
        user = request.user
        # print(user)
        print(request.data)
        # print("Headers:", request.headers)
        # print("User:", request.user)
        # print("Is authenticated:", request.user.is_authenticated)
        # Try to get or create the profile for the user
        profile, created = ProfileTable.objects.get_or_create(loginid=user)

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
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

    def delete(self, request, fooditem_id):
        try:
            wishlist_item = WishlistTable.objects.get(userid=request.user, fooditem_id=fooditem_id)
            wishlist_item.delete()
            return Response({'message': 'Item removed from wishlist.'}, status=status.HTTP_200_OK)
        except WishlistTable.DoesNotExist:
            return Response({'error': 'Item not found in wishlist.'}, status=status.HTTP_404_NOT_FOUND)


class WishlistItemsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        wishlist_items = WishlistTable.objects.filter(userid=request.user).select_related('fooditem')
        serializer = WishlistSerializer(wishlist_items, many=True)
        return Response({'wishlist_items': serializer.data}, status=status.HTTP_200_OK)



    # cart view ...............................
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        fooditem_id = data.get('fooditem')
        quantity = data.get('quantity')
        addon_id = data.get('addon')
        instruction = data.get('instruction')

        if not fooditem_id or not quantity:
            return Response({'error': 'fooditem and quantity are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            fooditem = ItemTable.objects.get(id=fooditem_id)
            addon = None
            if addon_id:
                addon = ItemTable.objects.get(id=addon_id)

            price = fooditem.price
            addon_price = addon.price if addon else 0.0
            total_price = (float(price) + float(addon_price)) * int(quantity)

            cart_item = CartTable.objects.create(
                userid=request.user,
                fooditem=fooditem,
                quantity=quantity,
                price=price,
                addon=addon,
                instruction=instruction,
                total_price=total_price
            )

            serializer = CartSerializer(cart_item)
            return Response({'message': 'Item added to cart.', 'item': serializer.data}, status=status.HTTP_201_CREATED)

        except ItemTable.DoesNotExist:
            return Response({'error': 'Invalid food item or addon.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Failed to add item.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, cart_item_id):
        try:
            cart_item = CartTable.objects.get(id=cart_item_id, userid=request.user)
            cart_item.delete()
            return Response({'message': 'Item removed from cart.'}, status=status.HTTP_200_OK)
        except CartTable.DoesNotExist:
            return Response({'error': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)


class UpdateNameAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            profile = ProfileTable.objects.get(loginid=request.user)
            serializer = ProfileNameUpdateSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Name updated successfully.', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ProfileTable.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)


class UpdateLocationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            profile = ProfileTable.objects.get(loginid=request.user)
            serializer = ProfileLocationUpdateSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Location updated successfully.', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ProfileTable.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        

class GetProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = ProfileTable.objects.get(loginid=request.user)
            serializer = ProfileTableSerializer(profile)
            return Response({'profile': serializer.data}, status=status.HTTP_200_OK)
        except ProfileTable.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

class CarouselAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        carousels = CarouselTable.objects.all()
        serializer = CarouselSerializer(carousels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SpotlightApiView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        spotlights = SpotlightTable.objects.all()
        serializer = SpotlightSerializer(spotlights, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProfileApiView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        profile = ProfileTable.objects.all()
        serializer = ProfileTableSerializer(profile, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 
    
class EditProfileAPIView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, pk):
        try:
            profile = ProfileTable.objects.get(pk=pk)
        except ProfileTable.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileTableSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItemListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        items = ItemTable.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class WishlistAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        wishlist = WishlistTable.objects.filter(userid=request.user)
        serializer = WishlistSerializer(wishlist, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = WishlistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(userid=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WishlistDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, pk):
        try:
            wishlist_item = WishlistTable.objects.get(id=pk, userid=request.user)
            wishlist_item.delete()
            return Response({"message": "Item removed from wishlist."}, status=status.HTTP_204_NO_CONTENT)
        except WishlistTable.DoesNotExist:
            return Response({"error": "Item not found in wishlist."}, status=status.HTTP_404_NOT_FOUND)

class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = CartTable.objects.filter(userid=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            quantity = int(request.data.get('quantity', 1))
            price = float(request.data.get('price', 0))
            total_price = price * quantity
            serializer.save(userid=request.user, total_price=total_price)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CartDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            cart_item = CartTable.objects.get(id=pk, userid=request.user)
        except CartTable.DoesNotExist:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartSerializer(cart_item, data=request.data, partial=True)
        if serializer.is_valid():
            quantity = int(request.data.get('quantity', cart_item.quantity))
            price = float(request.data.get('price', cart_item.price))
            total_price = price * quantity
            serializer.save(total_price=total_price)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            cart_item = CartTable.objects.get(id=pk, userid=request.user)
            cart_item.delete()
            return Response({"message": "Cart item removed."}, status=status.HTTP_204_NO_CONTENT)
        except CartTable.DoesNotExist:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
