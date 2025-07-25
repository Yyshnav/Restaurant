from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from Accountapp.models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.http import HttpResponseRedirect



# Create your views here.

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log in the user
            login(request, user)

            # If user is superuser, ensure they have ADMIN role
            if user.is_superuser:
                admin_role, _ = UserRole.objects.get_or_create(role='ADMIN')
                if not user.user_roles.filter(role='ADMIN').exists():
                    user.user_roles.add(admin_role)
                return HttpResponse('''<script>alert("Welcome Back");window.location='/dashboard'</script>''')

            # Check user's roles
            user_roles = user.user_roles.all()
            if user_roles.exists():
                role = user_roles.first().role.upper()

                # Redirect based on role
                if role == 'ADMIN':
                    return redirect('dashboard')
                elif role == 'MANAGER':
                    return redirect('manager_dashboard')
                elif role == 'WAITER':
                    return redirect('waiter_dashboard')
                elif role == 'KITCHEN':
                    return redirect('kitchen_dashboard')

            # Fallback if no role
            return redirect('default_dashboard')

        # Invalid login
        return render(request, 'login.html', {'error': 'Invalid credentials'})


class LogoutView(View):
    def get(self, request):
        logout(request)
        response = HttpResponse('''<script>alert("logged out successfully");window.location='/'</script>''')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    

class DashboardView(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):
        user = request.user

        if not user.is_authenticated:
            return redirect('login')

        if user.user_roles.filter(role='ADMIN').exists() or user.is_superuser:
            return render(request, 'index.html')

        return redirect('login')
 
    
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
def admin_dashboard(request):
    if request.user.user_roles.filter(role='ADMIN').exists() or request.user.is_superuser:
        return render(request, 'index.html')
    return redirect('login')

    
class AddBranchView(View):
    def get(self, request):
        return render(request, 'addbranch.html')
    
    def post(self, request):
        name = request.POST.get('branch_name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        floor = request.POST.get('floor')
        fssai_lic_no = request.POST.get('fssai_lic_no')
        image = request.FILES.get('image')  # For uploaded file

        BranchTable.objects.create(
            name=name,
            address=address,
            place=city,
            email=email,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            floors=floor,
            image=image,
            fssai_lic_no=fssai_lic_no
        )

        return redirect('view-branch')  


# class AddCategoryView(View):
#     def get(self, request):
#         return render(request, 'addCategory.html')
    
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
        c = BranchTable.objects.all()
        return render(request, 'registerstaff.html', {'branches': c})

class ViewBranchReportView(View):
    def get(self, request):
        return render(request, 'Viewbranch-report.html')

class ViewBranchView(LoginRequiredMixin, View):
    def get(self, request):
        c = BranchTable.objects.all().order_by('-created_at')
        return render(request, 'ViewBranch.html', {'branches':c})
    
class DeleteBranchView(View):
    def get(self, request, branch_id):
        try:
            branch = BranchTable.objects.get(id=branch_id)
            branch.delete()
            return HttpResponse('''<script>alert('delete successfully');window.location='/view-branch'</script>''')
        except BranchTable.DoesNotExist:
            return HttpResponse('''<script>alert('Branch not found');window.location='/view-branch'</script>''')
        
class EditBranchView(View):
    def get(self, request, branch_id):
        branch = get_object_or_404(BranchTable, id=branch_id)
        return render(request, 'editbranch.html', {'branch': branch})

    def post(self, request, branch_id):
        branch = get_object_or_404(BranchTable, id=branch_id)

        branch.name = request.POST.get('branch_name')
        branch.address = request.POST.get('address')
        branch.place = request.POST.get('city')
        branch.email = request.POST.get('email')
        branch.phone = request.POST.get('phone')
        branch.latitude = request.POST.get('latitude')
        branch.longitude = request.POST.get('longitude')
        branch.floors = request.POST.get('floor')
        branch.fssai_lic_no = request.POST.get('fssai_lic_no')

        if request.FILES.get('image'):
            branch.image = request.FILES.get('image')

        branch.save()
        return redirect('view-branch')  # change to your actual list view name

class ViewcarouselView(View):
    def get(self, request):
        return render(request, 'viewcarousel.html')
    
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from Accountapp.models import CategoryTable, SubCategoryTable, SubSubCategoryTable
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import base64
from django.core.files.base import ContentFile
import uuid

@method_decorator(csrf_exempt, name='dispatch')
class CategoryManagerView(View):
    def get(self, request):
        categories = []
        for cat in CategoryTable.objects.all():
            categories.append({
                "id": f"cat-{cat.id}",
                "name": cat.name,
                "img": cat.image.url if cat.image else "",
                "parent": None
            })
            for sub in cat.subcategories.all():
                categories.append({
                    "id": f"sub-{sub.id}",
                    "name": sub.name,
                    "img": "",  # No image in SubCategory model
                    "parent": f"cat-{cat.id}"
                })
                for subsub in sub.subsubcategories.all():
                    categories.append({
                        "id": f"subsub-{subsub.id}",
                        "name": subsub.name,
                        "img": "",  # No image in SubSubCategory model
                        "parent": f"sub-{sub.id}"
                    })

        return render(request, 'viewcategory.html', {'categories_json': categories})

    def post(self, request):
        import json
        data = json.loads(request.body)

        name = data.get("name")
        image_data = data.get("img")
        parent_id = data.get("parent")

        saved_image = None
        if image_data and image_data.startswith("data:image"):
            format, imgstr = image_data.split(';base64,') 
            ext = format.split('/')[-1]  
            file_name = f"{uuid.uuid4()}.{ext}"
            saved_image = ContentFile(base64.b64decode(imgstr), name=file_name)

        if not parent_id:
            cat = CategoryTable.objects.create(name=name)
            if saved_image:
                cat.image = saved_image
                cat.save()
            return JsonResponse({"status": "success", "id": f"cat-{cat.id}"})

        elif parent_id.startswith("cat-"):
            cat_id = parent_id.replace("cat-", "")
            sub = SubCategoryTable.objects.create(name=name, category_id=cat_id)
            return JsonResponse({"status": "success", "id": f"sub-{sub.id}"})

        elif parent_id.startswith("sub-"):
            sub_id = parent_id.replace("sub-", "")
            subsub = SubSubCategoryTable.objects.create(name=name, subcategory_id=sub_id)
            return JsonResponse({"status": "success", "id": f"subsub-{subsub.id}"})

        return JsonResponse({"status": "error"})

    
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