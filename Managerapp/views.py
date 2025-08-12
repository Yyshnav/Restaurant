from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from Accountapp.models import *

# Create your views here.

class ManagerDash(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return redirect('login')
        if user.user_roles.filter(role='MANAGER').exists():
            return render(request, 'dashboard.html')
        return redirect('login')
    
class CrediUser(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):
        return render(request, 'crediusers.html')

class DishesView(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):
        return render(request, 'dishes.html')
    
class OnlineOrdersView(View):
    def get(self, request):
        return render(request, 'onlineOrders.html')
    
class PrinterView(View):
    def get(self, request):
        categories = CategoryTable.objects.prefetch_related('subcategories').all()
        printers = PrinterTable.objects.all()

        return render(request, 'printer.html', {
            'categories': categories,
            'printers': printers
        })

class AddTableView(View):
    def get(self, request):
        return render(request, 'table.html')
    
class TakeOrdersView(View):
    def get(self, request):
        return render(request, 'take-order.html')
    
class ViewOrderView(View):
    def get(self, request):
        return render(request, 'view-orders.html')
    
class ViewStaff(View):
    def get(self, request):
        return render(request, 'viewstaffman.html')