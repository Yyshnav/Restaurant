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
from django.contrib.auth.hashers import make_password



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
    
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect
from django.contrib import messages

    
class RegisterStaffView(View):
    def get(self, request):
        branches = BranchTable.objects.all()
        return render(request, 'registerstaff.html', {'branches': branches})

    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        branch_id = request.POST.get('branch')
        password = request.POST.get('password')
        role = request.POST.get('role')  # manager, waiter, deliveryboy
        qualification = request.POST.get('qualification')

        idproof = request.FILES.get('employee_id')
        image = request.FILES.get('employee_image')
        license_pic = request.FILES.get('license')

        # Check if email already exists
        if LoginTable.objects.filter(username=email).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect('register_staff')

        try:
            branch = BranchTable.objects.get(id=branch_id)
        except BranchTable.DoesNotExist:
            messages.error(request, "Invalid branch selected.")
            return redirect('view-staff')

        # Create Login User
        login_user = LoginTable.objects.create(
            username=email,
            email=email,
            phone=phone,
            password=make_password(password),
            is_active=True,
            created_at=timezone.now(),
        )

        # Assign Role
        try:
            role_obj = UserRole.objects.get(role__iexact=role.upper())
        except UserRole.DoesNotExist:
            role_obj = UserRole.objects.create(role=role.upper())
        login_user.user_roles.add(role_obj)

        # Role-based Table Creation
        if role == 'manager':
            ManagerTable.objects.create(
                userid=login_user,
                BranchID=branch,
                name=name,
                phone=phone,
                address=address,
                email=email,
                image=image,
                idproof=idproof,
                qualification=qualification
            )
        elif role == 'waiter':
            WaiterTable.objects.create(
                userid=login_user,
                BranchID=branch,
                name=name,
                phone=phone,
                address=address,
                email=email,
                image=image,
                idproof=idproof
            )
        elif role == 'deliveryboy':
            DeliveryBoyTable.objects.create(
                userid=login_user,
                branch=branch,
                name=name,
                phone=phone,
                address=address,
                email=email,
                image=image,
                idproof=idproof,
                license=license_pic
            )

        # Send Password to Email
        subject = "Your Restaurant Staff Login Details"
        message = f"Hello {name},\n\nYour login account has been created.\n\nUsername: {email}\nPassword: {password}\n\nPlease keep it safe."
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except Exception as e:
            messages.warning(request, f"User created but failed to send email: {str(e)}")

        messages.success(request, "Staff registered successfully and login details sent via email.")
        return redirect('registerstaff')

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
        return redirect('view-branch')  

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
import json


@method_decorator(csrf_exempt, name='dispatch')
class CategoryManagerView(View):
    def get(self, request):
        data = []

        for cat in CategoryTable.objects.all():
            data.append({
                "id": f"cat-{cat.id}",
                "name": cat.name,
                "img": cat.image.url if cat.image else "",
                "parent": None
            })
            for sub in cat.subcategories.all():
                data.append({
                    "id": f"sub-{sub.id}",
                    "name": sub.name,
                    "img": sub.image.url if sub.image else "",
                    "parent": f"cat-{cat.id}"
                })
                for subsub in sub.subsubcategories.all():
                    data.append({
                        "id": f"subsub-{subsub.id}",
                        "name": subsub.name,
                        "img": subsub.image.url if subsub.image else "",
                        "parent": f"sub-{sub.id}"
                    })

        # If it's an AJAX request, return JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"categories": data})

        # Else return full HTML
        return render(request, "viewcategory.html", {
            "categories_json": json.dumps(data)
        })


    def post(self, request):
        name = request.POST.get("name")
        parent_id = request.POST.get("parent")
        image_file = request.FILES.get("img")

        if not parent_id:
            # Main Category
            cat = CategoryTable.objects.create(name=name)
            if image_file:
                cat.image = image_file
                cat.save()
            return JsonResponse({"status": "success", "id": f"cat-{cat.id}"})

        elif parent_id.startswith("cat-"):
            # Sub Category
            cat_id = parent_id.replace("cat-", "")
            sub = SubCategoryTable.objects.create(name=name, category_id=cat_id)
            if image_file:
                sub.image = image_file
                sub.save()
            return JsonResponse({"status": "success", "id": f"sub-{sub.id}"})

        elif parent_id.startswith("sub-"):
            # Sub Sub Category
            sub_id = parent_id.replace("sub-", "")
            subsub = SubSubCategoryTable.objects.create(name=name, subcategory_id=sub_id)
            if image_file:
                subsub.image = image_file
                subsub.save()
            return JsonResponse({"status": "success", "id": f"subsub-{subsub.id}"})

        return JsonResponse({"status": "error", "message": "Invalid parent ID"})

# views.py
from django.shortcuts import render
from django.http import JsonResponse
from Accountapp.models import CategoryTable, SubCategoryTable, SubSubCategoryTable
from django.views.decorators.csrf import csrf_exempt

def category_page(request):
    categories = CategoryTable.objects.all().prefetch_related('subcategories__subsubcategories')
    return render(request, 'category_page.html', {
        'categories': categories
    })

@csrf_exempt
def add_category_ajax(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        cat = CategoryTable.objects.create(name=name, image=image)
        return JsonResponse({'status': 'success', 'id': cat.id})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def add_subcategory_ajax(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        cat_id = request.POST.get('category_id')
        image = request.FILES.get('image')
        sub = SubCategoryTable.objects.create(name=name, image=image, category_id=cat_id)
        return JsonResponse({'status': 'success', 'id': sub.id})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def add_subsubcategory_ajax(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        subcat_id = request.POST.get('subcategory_id')
        image = request.FILES.get('image')
        subsub = SubSubCategoryTable.objects.create(name=name, image=image, subcategory_id=subcat_id)
        return JsonResponse({'status': 'success', 'id': subsub.id})
    return JsonResponse({'status': 'error'}, status=400)



from django.http import JsonResponse, HttpResponseBadRequest

def delete_category(request, type, pk):
    if request.method == 'POST':
        try:
            pk = int(pk)
        except ValueError:
            return HttpResponseBadRequest('Invalid ID')

        model = {
            'main': CategoryTable,
            'sub': SubCategoryTable,
            'subsub': SubSubCategoryTable,
        }.get(type)

        if model:
            try:
                model.objects.get(id=pk).delete()
                return JsonResponse({'status': 'success'})
            except model.DoesNotExist:
                return JsonResponse({'status': 'not_found'}, status=404)

    return JsonResponse({'status': 'failed'}, status=400)



    
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
        managers = ManagerTable.objects.select_related('userid').all()
        waiters = WaiterTable.objects.select_related('userid').all()
        deliveryboys = DeliveryBoyTable.objects.select_related('userid').all()

        staff_list = []

        for m in managers:
            staff_list.append({
                'name': m.name,
                'email': m.email,
                'role': 'Manager',
                'userid': m.userid
            })

        for w in waiters:
            staff_list.append({
                'name': w.name,
                'email': w.email,
                'role': 'Waiter',
                'userid': w.userid
            })

        for d in deliveryboys:
            staff_list.append({
                'name': d.name,
                'email': d.email,
                'role': 'Delivery Boy',
                'userid': d.userid
            })

        return render(request, 'viewStaff.html', {'staffs': staff_list})



@csrf_exempt
def toggle_staff_status(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        status = request.POST.get('status') == 'true'

        try:
            user = LoginTable.objects.get(id=user_id)
            user.is_active = status
            user.save()
            return JsonResponse({'success': True, 'message': 'Status updated successfully'})
        except LoginTable.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})



class DeleteStaff(View):
    def get(self, request, id):
        try:
            user = get_object_or_404(LoginTable, id=id)

            # Try deleting from each table (if user is found in that table)
            manager = ManagerTable.objects.filter(userid=user).first()
            waiter = WaiterTable.objects.filter(userid=user).first()
            delivery_boy = DeliveryBoyTable.objects.filter(userid=user).first()

            if manager:
                manager.delete()
            elif waiter:
                waiter.delete()
            elif delivery_boy:
                delivery_boy.delete()

            # Now delete the user from LoginTable
            user.delete()

            messages.success(request, "Staff deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting staff: {str(e)}")

        return redirect('view-staff')  # Replace with your actual staff list view name
    

from django.shortcuts import render, redirect, get_object_or_404


class EditStaffView(View):
    def get(self, request, id):
        staff = None
        role = None

        try:
            staff = ManagerTable.objects.get(userid=id)
            role = 'manager'
        except ManagerTable.DoesNotExist:
            try:
                staff = WaiterTable.objects.get(userid=id)
                role = 'waiter'
            except WaiterTable.DoesNotExist:
                staff = get_object_or_404(DeliveryBoyTable, userid=id)
                role = 'deliveryboy'

        branches = BranchTable.objects.all()
        return render(request, 'editstaff.html', {
            'staff': staff,
            'role': role,
            'branches': branches
        })


    def post(self, request, id):
        login_user = get_object_or_404(LoginTable, id=id)
        role = request.POST.get('role')

        login_user.username = request.POST.get('name')
        login_user.phone = request.POST.get('phone')
        if request.POST.get('password'):
            login_user.set_password(request.POST.get('password'))
        login_user.save()

        branch = get_object_or_404(BranchTable, id=request.POST.get('branch'))

        data = {
            'name': request.POST.get('name'),
            'phone': request.POST.get('phone'),
            'email': request.POST.get('email'),
            'address': request.POST.get('address'),
            'branch' if role == 'deliveryboy' else 'BranchID': branch,
        }

        if 'employee_image' in request.FILES:
            data['image'] = request.FILES['employee_image']
        if 'employee_id' in request.FILES:
            data['idproof'] = request.FILES['employee_id']

        if role == 'manager':
            data['qualification'] = request.POST.get('qualification')
            ManagerTable.objects.filter(userid=id).update(**data)
        elif role == 'waiter':
            WaiterTable.objects.filter(userid=id).update(**data)
        elif role == 'deliveryboy':
            if 'license' in request.FILES:
                data['license'] = request.FILES['license']
            DeliveryBoyTable.objects.filter(userid=id).update(**data)

        messages.success(request, "Staff updated successfully")
        return redirect('view-staff')  # Replace with your actual view name
