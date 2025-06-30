"""
URL configuration for Restaurant project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from Userapp.views import *

urlpatterns = [

    path('/', admin.site.urls),
    #auth

    path('send_otp/',SendOTPView.as_view(), name='send_otp'),
    path('verify_otp/',VerifyOTPView.as_view(), name='verify-otp'), 
    path('add_basic_details/',AddBasicDetailsView.as_view(), name='add_basic_details'),


    path('wishlist/', WishlistItemsView.as_view(), name='wishlist-items'),
    path('wishlist/add/', AddToWishlistView.as_view(), name='add-to-wishlist'),
    path('wishlist/remove/<int:fooditem_id>/', RemoveFromWishlistView.as_view(), name='remove-from-wishlist'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/remove/<int:cart_item_id>/', RemoveFromCartView.as_view(), name='remove-from-cart'),


]
