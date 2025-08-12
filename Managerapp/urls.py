
from django.urls import path

from .views import *

urlpatterns = [
    path('managerdash/', ManagerDash.as_view(), name='manager_dashboard'),
    path('crediusers/', CrediUser.as_view(), name='credi_users'),
    path('dishes/', DishesView.as_view(), name='dishes'),
    path('onlineorders/', OnlineOrdersView.as_view(), name='online_orders'),
    path('printer/', PrinterView.as_view(), name='printer'),
    path('addtable/', AddTableView.as_view(), name='add_table'),
    path('takeorders/', TakeOrdersView.as_view(), name='take_orders'),
    path('vieworders/', ViewOrderView.as_view(), name='view_orders'),
    path('viewstaff/', ViewStaff.as_view(), name='view_staff'),
]
