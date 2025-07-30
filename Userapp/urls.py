from django.urls import path

from Userapp.views import *

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [

    
    #auth

    path('send_otp/',SendOTPView.as_view(), name='send_otp'),
    path('verify_otp/',VerifyOTPView.as_view(), name='verify-otp'), 
    path('add_basic_details/',AddBasicDetailsView.as_view(), name='add_basic_details'),


    # path('wishlist/', WishlistItemsView.as_view(), name='wishlist-items'),
    # path('wishlist/add/', AddToWishlistView.as_view(), name='add-to-wishlist'),
    # path('wishlist/remove/<int:fooditem_id>/', RemoveFromWishlistView.as_view(), name='remove-from-wishlist'),
    # path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    # path('cart/remove/<int:cart_item_id>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('carousel/',CarouselAPIView.as_view(), name='carousel'),
    path('spotlight/',SpotlightApiView.as_view(), name='spotlight'),
    # path('profile/', ProfileApiView.as_view(), name = 'profile'),
    path('items/', ItemListAPIView.as_view(), name='item-list'),
    path('branchitems/', BranchItemsAPIView.as_view(), name='item-list'),
    path('wishlist/', WishlistAPIView.as_view(), name='wishlist'),
    path('wishlist/<int:pk>/', WishlistDeleteAPIView.as_view(), name='wishlist-delete'),
    path('cartitems/', CartAPIView.as_view(), name='cart'),
    path('cart/<int:pk>/', CartDeleteAPIView.as_view(), name='cart-detail'),
    path('changeaddress/<int:address_id>/', ChangeAddressAPIView.as_view(), name='change-address'),
    path('trackorder/<int:order_id>/', TrackDeliveryLocationAPI.as_view(), name='track-order'),
    path('profile/', ProfileAPIView.as_view(), name='user-profile'),
    path('profile/update/', UpdateUserProfileByIdAPIView.as_view(), name='update-user-profile'),
    path('coupon/', CouponListAPIView.as_view(), name='coupon-list'),
    path('applycoupon/', ApplyCouponAPIView.as_view(), name='apply-coupon'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('update-fcm-token/', UpdateFCMTokenView.as_view(), name='update_fcm_token'),
    path('personalized/', PersonalizedRecommendationAPIView.as_view(), name='personalized'),
    path('placeorder/', PlaceOrderAPIView.as_view(), name='placeorder'),
]
