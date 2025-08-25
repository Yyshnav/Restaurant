
from django.urls import path

from Managerapp.views import *
from . import views


urlpatterns = [
    path('managerdash/', ManagerDash.as_view(), name='manager_dashboard'),
    path('crediusers/', CrediUser.as_view(), name='credi_users'),
    path('dishes/', DishesView.as_view(), name='dishes'),
    path('onlineorders/', OnlineOrdersView.as_view(), name='online_orders'),
    path('printer/', PrinterView.as_view(), name='printer'),
    path('addtable/', AddTableView.as_view(), name='add_table'),
    path('takeorders/', TakeOrdersView.as_view(), name='take_orders'),
    path("orders/", OrdersListView.as_view(), name="orders"),
    path('viewstaffman/', ViewStaff.as_view(), name='view_staff'),
    path('printers/add/', AddPrinterView.as_view(), name='add_printer'),
    path('printer/delete/<int:pk>/', views.delete_printer, name='delete_printer'),
    path('printers/edit/<int:pk>/', views.edit_printer, name='edit_printer'),
    path('variant/<int:variant_id>/edit/', views.edit_variant_price, name='edit_variant_price'),
    path('dish/<int:pk>/toggle/', views.toggle_availability, name='toggle_availability'),
    path('staff/<str:staff_id>/', StaffDetailView.as_view(), name='staff_detail'),
    path("save-table/", SaveTableView.as_view(), name="save_table"),
    path('delete-table/<int:table_id>/', DeleteTableView.as_view(), name='delete_table'),
    path("save-order/", save_order, name="save_order"),
    path('orders/accept/<int:order_id>/', AcceptOrderView.as_view(), name='accept_order'),
    path('assigndeliveryboy/<int:order_id>/', AssignDeliveryBoyView.as_view(), name='assign_delivery_boy'),
    path('orders/reject/<int:order_id>/', RejectOrderView.as_view(), name='reject_order'),



]
