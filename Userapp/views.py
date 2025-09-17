import datetime
from multiprocessing.connection import Client
from time import timezone
import traceback
from django.shortcuts import get_object_or_404, render
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random
from Accountapp.models import AddonTable, AddressTable, BranchTable, CarouselTable, CartTable, CouponTable, DeliveryBoyTable, ItemTable, ItemVariantTable, LoginTable, OfferTable, OrderItemTable, OrderTable, PaymentTable, SpotlightTable, UserRole, WishlistTable
from django.conf import settings
from Adminapp.serializer import BranchTableSerializer, CarouselSerializer, CarouselWithOffersSerializer, CouponSerializer, ItemSerializer, ItemVariantSerializer, OfferTableSerializer, OrderTableSerializer, SpotlightSerializer
# from Deliveryboyapp.serializer import OrderSerializer
from Deliveryboyapp.serializer import TrackOrderSerializer
from Userapp.serializer import AddressTableSerializer, AddressUpdateSerializer, OrderHistorySerializer, PlaceOrderSerializer, ProfileTableSerializer, UserOrderSerializer
from Userapp.serializer import AddressTableSerializer, AddressUpdateSerializer, OrderRetrieveSerializer, PlaceOrderSerializer, ProfileTableSerializer, RatingSerializer, UserOrderSerializer
# from twilio.rest import Client
from Accountapp.models import ProfileTable
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework.permissions import IsAuthenticated
import requests
import secrets
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from Userapp.serializer import CartSerializer, ProfileLocationUpdateSerializer, ProfileNameUpdateSerializer, ProfileTableSerializer, WishlistSerializer
from math import radians, cos, sin, asin, sqrt
from django.db.models import Q
from django.db import transaction

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
#         print("SendOTPView POST called")  # DEBUG: View is hit
#         try:
#             phone = request.data.get('phone')
#             print("Phone received:", phone)  # DEBUG

#             if not phone:
#                 return Response({'error': 'Phone number is required.'}, status=400)

#             otp = random.randint(1000, 9999)
#             print("Generated OTP:", otp)  # DEBUG

#             # -------------------------
#             # Database: Create or update user
#             try:
#                 user, created = LoginTable.objects.get_or_create(
#                     phone=phone,
#                     defaults={
#                         'username': phone,
#                         'otp': str(otp)
#                     }
#                 )
#                 print(f"User {'created' if created else 'exists'}:", user)  # DEBUG

#                 # Assign default role if new user
#                 if created and not user.user_roles.exists():
#                     default_role = UserRole.objects.filter(role="student").first()
#                     if default_role:
#                         user.user_roles.add(default_role)
#                         print("Default role assigned")  # DEBUG

#                 # Update OTP for existing user
#                 if not created:
#                     user.otp = str(otp)
#                     user.save()
#                     print("OTP updated for existing user")  # DEBUG

#             except Exception as e:
#                 print("Database Exception:", e)
#                 traceback.print_exc()
#                 return Response({
#                     'error': 'Database error',
#                     'details': str(e)
#                 }, status=500)

#             # -------------------------
#             # SMS: Send OTP via Fast2SMS
#             api_key = getattr(settings, "FAST2SMS_API_KEY", None)
#             print("API key:", api_key)  # DEBUG
#             if not api_key:
#                 return Response({'error': 'API key missing'}, status=500)

#             payload = {
#                 "route": "otp",
#                 "variables_values": str(otp),
#                 "numbers": phone.replace('+91', '')  # 10-digit number
#             }
#             print("Payload for Fast2SMS:", payload)  # DEBUG

#             try:
#                 response = requests.post(
#                     "https://www.fast2sms.com/dev/bulkV2",
#                     json=payload,
#                     headers={'authorization': api_key, 'Content-Type': "application/json"}
#                 )
#                 print("Fast2SMS response:", response.text)  # DEBUG

#                 if response.status_code != 200:
#                     return Response({
#                         'error': 'Failed to send OTP',
#                         'status_code': response.status_code,
#                         'details': response.text
#                     }, status=500)

#             except Exception as e:
#                 print("SMS Exception:", e)
#                 traceback.print_exc()
#                 return Response({
#                     'error': 'SMS sending failed',
#                     'details': str(e)
#                 }, status=500)

#             return Response({'message': 'OTP sent successfully', 'otp': otp}, status=200)

#         except Exception as e:
#             print("Unhandled Exception:", e)
#             traceback.print_exc()
#             return Response({
#                 'error': 'Something went wrong',
#                 'details': str(e)
#             }, status=500)
        
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
                user.otp_verified = True
                user.save()

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                print(f"Fetching profile for user with phone: {phone}")

                
                try:
                    profile = ProfileTable.objects.get(loginid=user)
                    print(f"Profile found for user {phone}: {profile}")
                    profile_data = {
                        "name": profile.name,
                        "phone": profile.phone,
                        "email": profile.email,
                        "dob": profile.dob,
                        "image": profile.image.url if profile.image else None,
                        "created_at": profile.created_at,
                        "updated_at": profile.updated_at,
                    }
                except ProfileTable.DoesNotExist:
                    profile_data = None

                return Response({
                    'message': 'OTP verified successfully.',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'profile': profile_data if profile_data else "No profile found for this user."
                }, status=status.HTTP_200_OK)

            else:
                return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        except LoginTable.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Database error.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
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
        serializer = ItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371  # Radius of Earth in KM
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return R * c
    
class BranchItemsAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        user_lat = request.data.get('latitude')
        user_lon = request.data.get('longitude')
        selected_branch_id = request.data.get('branch_id')
        print(request.data)

        # Get all branches
        all_branches = BranchTable.objects.exclude(latitude=None).exclude(longitude=None)

        # If branch_id is provided, use that branch
        if selected_branch_id:
            try:
                selected_branch = BranchTable.objects.get(id=selected_branch_id)
            except BranchTable.DoesNotExist:
                return Response({'error': 'Branch not found'}, status=404)
        else:
            # Calculate nearest branch using user location
            if not user_lat or not user_lon:
                return Response({'error': 'Location is required if branch_id not provided'}, status=400)

            user_lat = float(user_lat)
            user_lon = float(user_lon)

            distances = []
            for branch in all_branches:
                dist = calculate_distance(user_lat, user_lon, branch.latitude, branch.longitude)
                distances.append((dist, branch))

            distances.sort(key=lambda x: x[0])
            selected_branch = distances[0][1] if distances else None

        if not selected_branch:
            return Response({'error': 'No branch selected or found'}, status=404)

        # Get items in selected branch
        items = ItemTable.objects.filter(branches=selected_branch)
        print(f"Found {items.count()} items in branch {selected_branch.name}", items.values())
        print('items======>:', ItemSerializer(items, many=True, context={'request': request}).data)

        return Response({
            'selected_branch': BranchTableSerializer(selected_branch).data,
            'all_branches': BranchTableSerializer(all_branches, many=True).data,
            'items': ItemSerializer(items, many=True, context={'request': request}).data, 
        })
  
# class WishlistAPIView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request):
#         userid = request.query_params.get('userid')
#         if not userid:
#             return Response({"error": "User ID is required."}, status=400)

#         wishlist = WishlistTable.objects.filter(userid_id=userid)
#         serializer = WishlistSerializer(wishlist, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         userid = request.data.get('userid')
#         fooditem_id = request.data.get('fooditem')

#         if not userid or not fooditem_id:
#             return Response({"error": "User ID and food item ID are required."}, status=400)

#         # Prevent duplicate wishlist entries
#         exists = WishlistTable.objects.filter(userid_id=userid, fooditem_id=fooditem_id).exists()
#         if exists:
#             return Response({"message": "Item already in wishlist."}, status=200)

#         WishlistTable.objects.create(userid_id=userid, fooditem_id=fooditem_id)
#         return Response({"message": "Item added to wishlist."}, status=201)

#     def delete(self, request):
#         wishlist_id = request.data.get('id')
#         if not wishlist_id:
#             return Response({"error": "Wishlist ID is required."}, status=400)

#         try:
#             wishlist = WishlistTable.objects.get(id=wishlist_id)
#             wishlist.delete()
#             return Response({"message": "Item removed from wishlist."}, status=200)
#         except WishlistTable.DoesNotExist:
#             return Response({"error": "Wishlist item not found."}, status=404)
    
class WishlistAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        wishlist = WishlistTable.objects.filter(userid=request.user)
        serializer = WishlistSerializer(wishlist, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = WishlistSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save(userid=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WishlistDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, id):
        return self._delete_item(request, id)

    def get(self, request, id):   # allow GET as delete (if you want GET also)
        return self._delete_item(request, id)

    def _delete_item(self, request, id):
        try:
            print(f"Attempting to delete wishlist items with FoodItem ID: {id}")

            # Fetch all matching rows
            wishlist_items = WishlistTable.objects.filter(userid=request.user, fooditem_id=id)

            if not wishlist_items.exists():
                print("No wishlist item found")
                return Response({"error": "Item not found in wishlist."}, status=status.HTTP_404_NOT_FOUND)

            # Delete all matching
            count, _ = wishlist_items.delete()
            print(f"Deleted {count} wishlist item(s)")

            return Response({"message": f"{count} item(s) removed from wishlist."}, status=status.HTTP_200_OK)

        except Exception as e:
            print("Error while deleting wishlist:", str(e))
            return Response({"error": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# class CartAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         cart_items = CartTable.objects.filter(userid=request.user)
#         serializer = CartSerializer(cart_items, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request):
#         serializer = CartSerializer(data=request.data)
#         print(request.data)
#         if serializer.is_valid():
#             fooditem = serializer.validated_data.get('fooditem')
#             quantity = serializer.validated_data.get('quantity', 1)
#             addon = serializer.validated_data.get('addon', None)

#             # Calculate price securely from backend
#             # base_price = fooditem.price or 0
#             # addon_price = addon.price if addon and hasattr(addon, 'price') else 0

#             # total_price = (base_price + addon_price) * quantity
#             base_price = float(fooditem.price) if fooditem and hasattr(fooditem, 'price') else 0.0
#             addon_price = float(addon.price) if addon and hasattr(addon, 'price') else 0.0
#             quantity = int(quantity)
#             total_price = (base_price + addon_price) * quantity

#             serializer.save(userid=request.user, total_price=total_price)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = (
            CartTable.objects
            .filter(userid=request.user)
            .select_related("fooditem", "variant")
            .prefetch_related("addon")   # this ensures addons are fetched efficiently
        )
        serializer = CartSerializer(cart_items, many=True)
        print("============================================================================",serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)



    def post(self, request):
        user = request.user

        variant_id = request.data.get('variant')
        fooditem_id = request.data.get('fooditem')
        addon_ids = request.data.get('addon', [])  # expect list of IDs
        quantity = request.data.get('quantity')

        # ✅ Validate quantity
        try:
            quantity = int(quantity)
            if quantity < 1:
                return Response({'error': 'Quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Validate food item
        try:
            fooditem = ItemTable.objects.get(id=fooditem_id)
        except ItemTable.DoesNotExist:
            return Response({'error': 'Food item not found'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Variant (optional)
        variant = None
        if variant_id:
            try:
                variant = ItemVariantTable.objects.get(id=variant_id)
            except ItemVariantTable.DoesNotExist:
                return Response({'error': 'Variant not found'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Addons (optional)
        addons = []
        if addon_ids:
            addons = list(AddonTable.objects.filter(id__in=addon_ids))
            if len(addons) != len(addon_ids):  # some invalid IDs
                return Response({'error': 'Some addons not found'}, status=status.HTTP_400_BAD_REQUEST)
        print('addons', addons)
        # ✅ Check for existing cart item (food + variant + exact addons)
        existing_item = CartTable.objects.filter(userid=user, fooditem=fooditem, variant=variant).first()

        if existing_item:
            existing_item.quantity = str(int(existing_item.quantity) + quantity)
            existing_item.save()
            if addons:
                existing_item.addon.set(addons)  # replace addons
            serializer = CartSerializer(existing_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            cart_item = CartTable.objects.create(
                userid=user,
                fooditem=fooditem,
                variant=variant,
                quantity=quantity,
            )
            if addons:
                cart_item.addon.set(addons)
            serializer = CartSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)




    
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
            return Response({"message": "Cart item and its addons deleted from DB."}, status=status.HTTP_204_NO_CONTENT)
        except CartTable.DoesNotExist:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
        
# class CartDeleteAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def put(self, request, pk):
#         try:
#             cart_item = CartTable.objects.get(id=pk, userid=request.user)
#         except CartTable.DoesNotExist:
#             return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

#         serializer = CartSerializer(cart_item, data=request.data, partial=True)
#         if serializer.is_valid():
#             quantity = int(request.data.get('quantity', cart_item.quantity))
#             price = float(request.data.get('price', cart_item.price))
#             total_price = price * quantity
#             serializer.save(total_price=total_price)
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         """Delete the entire cart item"""
#         try:
#             cart_item = CartTable.objects.get(id=pk, userid=request.user)
#             cart_item.delete()
#             return Response({"message": "Cart item removed."}, status=status.HTTP_204_NO_CONTENT)
#         except CartTable.DoesNotExist:
#             return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)


class CartAddonDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, cart_id, addon_id):
        """Delete a specific addon from a cart item"""
        try:
            # 🔹 Get the cart item belonging to this user
            cart_item = CartTable.objects.get(id=cart_id, userid=request.user)
        except CartTable.DoesNotExist:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            # 🔹 Check if the addon exists in DB
            addon = AddonTable.objects.get(id=addon_id)
        except AddonTable.DoesNotExist:
            return Response({"error": "Addon not found."}, status=status.HTTP_404_NOT_FOUND)

        # 🔹 Check if this addon is actually attached to this cart item
        if addon in cart_item.addon.all():
            cart_item.addon.remove(addon)   # ✅ remove relation
            cart_item.save()
            return Response({"message": f"Addon '{addon.name}' removed from cart."},
                            status=status.HTTP_200_OK)
        else:
            return Response({"error": "Addon not attached to this cart item."},
                            status=status.HTTP_404_NOT_FOUND)


class ChangeAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, address_id):
        user = request.user
        address = get_object_or_404(AddressTable, id=address_id, userid=user)
        serializer = AddressUpdateSerializer(address, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Address updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TrackDeliveryLocationAPI(APIView):
    def get(self, request, order_id):
        try:
            order = OrderTable.objects.get(id=order_id)
            delivery = order.deliveryid
            if delivery:
                data = {
                    'name': delivery.name,
                    'latitude': delivery.latitude,
                    'longitude': delivery.longitude,
                    'phone': delivery.phone
                }
                return Response(data)
            else:
                return Response({'error': 'No delivery person assigned.'}, status=status.HTTP_404_NOT_FOUND)
        except OrderTable.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        

class PersonalizedRecommendationAPIView(APIView):
    # authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        keyword = request.data.get('search_keyword', '').strip()
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        recommendations = ItemTable.objects.all()

        # 1️⃣ FILTER BY NEARBY BRANCH IF LOCATION IS GIVEN
        if latitude and longitude:
            try:
                latitude = float(latitude)
                longitude = float(longitude)
                nearby_branch_ids = []

                branches = BranchTable.objects.exclude(latitude=None).exclude(longitude=None)
                for branch in branches:
                    dist = calculate_distance(latitude, longitude, branch.latitude, branch.longitude)
                    if dist <= 10:  # radius in km
                        nearby_branch_ids.append(branch.id)

                if nearby_branch_ids:
                    recommendations = recommendations.filter(branches__id__in=nearby_branch_ids)
            except ValueError:
                pass  # ignore invalid lat/lon

        # 2️⃣ FILTER BY SEARCH KEYWORD
        if keyword:
            recommendations = recommendations.filter(
                Q(name__icontains=keyword) |
                Q(description__icontains=keyword)
            )

        # 3️⃣ FILTER BY USER HISTORY BASED ON TOKEN
        user = request.user
        try:
            login_user = LoginTable.objects.get(id=user.id)

            # Wishlist-based
            wishlist_item_ids = WishlistTable.objects.filter(userid=login_user).values_list('fooditem_id', flat=True)

            # Order history-based
            ordered_item_ids = OrderItemTable.objects.filter(order__userid__loginid=login_user).values_list('itemname_id', flat=True)

            # Combine history
            preferred_ids = set(wishlist_item_ids) | set(ordered_item_ids)

            if preferred_ids:
                recommendations = recommendations.filter(
                    Q(id__in=preferred_ids) |
                    Q(category__items__id__in=preferred_ids)
                ).distinct()

        except LoginTable.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=404)

        recommendations = recommendations.distinct().order_by('-fast_delivery', '-newest')[:20]
        serialized = ItemSerializer(recommendations, many=True)
        return Response({'recommendations': serialized.data})
    
class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("#####################################################################",request.user.id)
        try:
            profile = ProfileTable.objects.get(loginid=request.user)
            serializer = ProfileTableSerializer(profile)
            
            return Response(serializer.data)
        except ProfileTable.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

    # def post(self, request):
    #     print(request.user.id)
    #     try:
    #         ProfileTable.objects.get(loginid=request.user)
    #         return Response({"error": "Profile already exists."}, status=400)
    #     except ProfileTable.DoesNotExist:
    #         data = request.data.copy()
    #         serializer = ProfileTableSerializer(data=data)
    #         if serializer.is_valid():
    #             serializer.save(loginid=request.user)  # Assign current user
    #             return Response(serializer.data, status=201)
    #         return Response(serializer.errors, status=400)


        
class UpdateUserProfileByIdAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            profile = ProfileTable.objects.get(loginid=request.user)
            serializer = ProfileTableSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()  # loginid won't be overwritten
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except ProfileTable.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)


class CouponListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        coupons = CouponTable.objects.filter(is_active=True)
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ApplyCouponAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        code = request.data.get('code')
        order_amount = float(request.data.get('order_amount', 0))

        try:
            coupon = CouponTable.objects.get(code=code, is_active=True)

            # Check valid date range
            now = datetime.now()
            valid_from = datetime.strptime(coupon.valid_from, "%Y-%m-%d")
            valid_to = datetime.strptime(coupon.valid_to, "%Y-%m-%d")
            if not (valid_from <= now <= valid_to):
                return Response({'error': 'Coupon not valid at this time.'}, status=400)

            # Check minimum order amount
            if coupon.min_order_amount and order_amount < coupon.min_order_amount:
                return Response({'error': f'Minimum order amount is {coupon.min_order_amount}.'}, status=400)

            # Check usage limit
            if coupon.usage_limit and coupon.used_count:
                if int(coupon.used_count) >= int(coupon.usage_limit):
                    return Response({'error': 'Coupon usage limit reached.'}, status=400)

            # Calculate discount
            discount = (order_amount * coupon.discount_percentage / 100)
            if coupon.max_discount_amount:
                discount = min(discount, coupon.max_discount_amount)

            return Response({
                'message': 'Coupon applied successfully.',
                'discount': round(discount, 2),
                'final_amount': round(order_amount - discount, 2),
                'coupon_id': coupon.id
            })

        except CouponTable.DoesNotExist:
            return Response({'error': 'Invalid coupon code.'}, status=404)
    
class UpdateFCMTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('fcm_token')
        if not token:
            return Response({'error': 'FCM token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            user.notification_token = token
            user.save()
            return Response({'message': 'FCM token updated successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


# class PlaceOrderAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         print("Request Data:", request.data)
#         serializer = OrderSerializer(data=request.data, context={"request": request})
#         if serializer.is_valid():
#             order = serializer.save()
#             return Response({"message": "Order placed successfully", "order_id": order.id})
#         return Response(serializer.errors, status=400)

# class PlaceOrderAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         print("Request Data:", request.data)
        
#         # Create a mutable copy of request.data
#         data = request.data.copy()
#         data['userid'] = request.user.id

#         serializer = OrderSerializer(data=data, context={"request": request})
#         if serializer.is_valid():
#             try:
#                 with transaction.atomic():
#                     order = serializer.save()
#                     order.calculate_totals()  # Calculate totals after order creation
#                     return Response({
#                         "message": "Order placed successfully",
#                         "order_id": order.id
#                     }, status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class PlaceOrderAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         print("Request Data:", request.data)
#         print("Authenticated User:", request.user)
#         print("Request User ID:", request.user.id)

#         if not request.user.is_authenticated:
#             return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

#         # Create a mutable copy of request.data
#         data = request.data.copy()
#         data['userid'] = request.user.id
#         print(data['userid'])
#         print("Modified Data:", data)

#         serializer = UserOrderSerializer(data=data, context={"request": request})
#         if serializer.is_valid():
#             try:
#                 with transaction.atomic():
#                     order = serializer.save()
#                     order.calculate_totals()
#                     print(f"Saved Order: ID={order.id}, UserID={order.userid_id}, Branch={order.branch_id}, Address={order.address_id}, Coupon={order.coupon_id}")
#                     return Response({
#                         "message": "Order placed successfully",
#                         "order_id": order.id
#                     }, status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 print(f"Error during order creation: {str(e)}")
#                 return Response({"error": f"Failed to create order: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         print("Serializer Errors:", serializer.errors)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PlaceOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print("Request Data:", request.data)
        print("Authenticated User:", request.user)
        print("Request User ID:", request.user.id)

        if not request.user.is_authenticated:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # ✅ Fetch the related ProfileTable instance
            profile = ProfileTable.objects.get(loginid=request.user)
        except ProfileTable.DoesNotExist:
            return Response({"error": "Profile not found for this user"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a mutable copy of request.data
        data = request.data.copy()
        data['userid'] = profile.loginid.id # ✅ Set correct ProfileTable ID
        print("Modified Data:", data)

        serializer = UserOrderSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    order = serializer.save()
                    order.calculate_totals()
                    print(f"Saved Order: ID={order.id}, UserID={order.userid_id}, Branch={order.branch_id}, Address={order.address_id}, Coupon={order.coupon_id}")
                    return Response({
                        "message": "Order placed successfully",
                        "order_id": order.id
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"Error during order creation: {str(e)}")
                return Response({"error": f"Failed to create order: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print("Serializer Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAddressView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, *args, **kwargs):
        address_id = kwargs.get('address_id')
        try:
            if address_id:
                # Retrieve a single address
                address = AddressTable.objects.get(id=address_id, userid=request.user.id)
                serializer = AddressTableSerializer(address)
                print(f"Retrieved address ID {address_id} for user ID {request.user.id}")
                return Response({
                    "message": "Address retrieved successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                # List all addresses for the user
                addresses = AddressTable.objects.filter(userid=request.user.id)
                serializer = AddressTableSerializer(addresses, many=True)
                print(f"Retrieved {len(addresses)} addresses for user ID {request.user.id}")
                return Response({
                    "message": "Addresses retrieved successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
        except AddressTable.DoesNotExist:
            print(f"Address ID {address_id} not found for user ID {request.user.id}")
            return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error retrieving addresses: {str(e)}")
            return Response({"error": f"Failed to retrieve addresses: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class TrackAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, orderid):
        # print('------------------------------------------------------')
        # print(f"Tracking order ID: {orderid} for user ID: {request.user.id}")
        try:
            profile = ProfileTable.objects.get(loginid=request.user)
        except ProfileTable.DoesNotExist:
            return Response({'success': False, 'message': 'User profile not found'}, status=404)
        
        try:
            order = OrderTable.objects.get(id=orderid, userid_id=profile)
            # print("User orders:", order)
            serializer = TrackOrderSerializer(order)
            print(f"Order details for tracking: {serializer.data}")
            return Response({'success': True, 'data': serializer.data})
        except OrderTable.DoesNotExist:
            return Response({'success': False, 'message': 'Order not found'}, status=404)
        
    class OrderHistoryView(APIView):
        permission_classes = [IsAuthenticated]

        def get(self, request, *args, **kwargs):
            try:
                profile = ProfileTable.objects.get(loginid=request.user)
            except ProfileTable.DoesNotExist:
                return Response({'error': 'Profile not found for this user'}, status=404)

            orders = OrderTable.objects.filter(userid=profile).order_by('-created_at')

            serializer = OrderHistorySerializer(orders, many=True)
            return Response({
                "success": True,
                "count": len(serializer.data),
                "orders": serializer.data
            }, status=200)

        

class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("Fetching user orders...")
        try:
            # Fetch the profile of the authenticated user
            profile = get_object_or_404(ProfileTable, loginid=request.user)
            # Fetch orders associated with the user's profile
            orders = OrderTable.objects.filter(userid=profile).order_by('-created_at')
            # Serialize the orders
            serializer = OrderRetrieveSerializer(orders, many=True)
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            print(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )




class FeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ratings = request.data.get('ratings', [])
        if not isinstance(ratings, list):
            return Response(
                {'status': 'error', 'message': 'Ratings must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )

        response_data = []
        for rating_data in ratings:
            serializer = RatingSerializer(data=rating_data)
            if serializer.is_valid():
                serializer.save(userid=request.user)  # set authenticated user
                response_data.append(serializer.data)
            else:
                return Response(
                    {'status': 'error', 'message': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {'status': 'success', 'data': response_data},
            status=status.HTTP_201_CREATED
        )

class CarouselOffersAPIView(APIView):
    """
    Fetch the carousel with the linked offer and item
    """

    def get(self, request, carousel_id):
        now = timezone.now()
        carousel = get_object_or_404(CarouselTable, id=carousel_id, is_active=True)

        # Ensure the offer is active
        if not carousel.offer or not carousel.offer.is_active:
            return Response({'error': 'No active offer linked to this carousel'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CarouselWithOffersSerializer(carousel)
        return Response(serializer.data, status=status.HTTP_200_OK)