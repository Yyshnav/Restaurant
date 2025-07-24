from django.shortcuts import render
from django.views import View

# Create your views here.

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')
    
class DashboardView(View):
    def get(self, request):
        return render(request, 'index.html')
    
class AddBranchView(View):
    def get(self, request):
        return render(request, 'addbranch.html')


class AddCategoryView(View):
    def get(self, request):
        return render(request, 'addCategory.html')
    
class AddDishView(View):
    def get(self, request):
        return render(request, 'addDish.html')

class AddCarouselView(View):
    def get(self, request):
        return render(request, 'carouselAdd.html')
    
class EditDishView(View):
    def get(self, request):
        return render(request, 'dish_edit.html')


class AddOfferView(View):
    def get(self, request):
        return render(request, 'offerAdd.html')
    
class RegisterStaffView(View):
    def get(self, request):
        return render(request, 'registerstaff.html')

class ViewBranchReportView(View):
    def get(self, request):
        return render(request, 'Viewbranch-report.html')

class ViewBranchView(View):
    def get(self, request):
        return render(request, 'ViewBranch.html')
    
class ViewcarouselView(View):
    def get(self, request):
        return render(request, 'viewcarousel.html')
    
class ViewCategoryView(View):
    def get(self, request):
        return render(request, 'viewcategory.html')
    
class ViewComplaintView(View):
    def get(self, request):
        return render(request, 'viewcomplaint.html')
    
class ViewDishesView(View):
    def get(self, request):
        return render(request, 'viewdishes.html')
    
class ViewOfferView(View):
    def get(self, request):
        return render(request, 'viewoffer.html')
    
class ViewStaffView(View):
    def get(self, request):
        return render(request,'viewStaff.html')