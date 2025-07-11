
from django.contrib import admin
from django.urls import path
from Deliveryboyapp.views import * 

urlpatterns = [
    path('delivery_login/',DeliveryBoyLoginAPIView.as_view(), name='delivery_login'),
    path('latestPendingOrdersAPIView/',LatestPendingOrdersAPIView.as_view(), name='latestPendingOrdersAPIView'),
    path('assignedOrdersAPIView/',AssignedOrdersAPIView.as_view(), name='lssignedOrdersAPIView'),
    path('updateOrderStatusAPIView/',UpdateOrderStatusAPIView.as_view(), name='updateOrderStatusAPIView'),
    path('orderDetailAPIView/<int:order_id>/',OrderDetailAPIView.as_view(), name='orderDetailAPIView'),
    path('deliveryBoyProfileAPIView/',DeliveryBoyProfileAPIView.as_view(), name='deliveryBoyProfileAPIView'),
    path('deliveryBoyProfileupdateAPIView/',DeliveryBoyProfileAPIView.as_view(), name='deliveryBoyProfileupdateAPIView'),
    path('changePasswordAPIView/',ChangePasswordAPIView.as_view(), name='changePasswordAPIView'),
    path('postComplaintAPIView/',PostComplaintAPIView.as_view(), name='postComplaintAPIView'),
    path('orderHistoryAPIView/',OrderHistoryAPIView.as_view(), name='orderHistoryAPIView'),  
    path('feedbackAPIView/',FeedbackAPIView.as_view(), name='feedbackAPIView'),  
    path('forgotPasswordAPIView/',ForgotPasswordAPIView.as_view(), name='forgotPasswordAPIView'),  
    path('verifyOTPAPIView/',VerifyOTPAPIView.as_view(), name='verifyOTPAPIView'),  
    path('resetPasswordAPIView/',ResetPasswordAPIView.as_view(), name='resetPasswordAPIView'),  
    path('logoutAPIView/',LogoutAPIView.as_view(), name='logoutAPIView'),    

]
