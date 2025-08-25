from datetime import date
from time import localtime
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
from datetime import datetime





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
                    return redirect('waiterdashboard')
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
    
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

class AddDishView(View):
    def get(self, request):
        categories = CategoryTable.objects.all()
        branches = BranchTable.objects.all()
        return render(request, 'addDish.html', {
            'categories': categories,
            'branches': branches,
        })

    def post(self, request):
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        subsubcategory_id = request.POST.get('subsubcategory')
        is_veg = request.POST.get('is_veg') == 'True'
        description = request.POST.get('description')
        price = request.POST.get('price') or 0
        inventory = request.POST.get('inventory') or 0
        calories = request.POST.get('calories') or 0
        preparation_time = float(request.POST.get('preparation_time') or 0)

        # Automatically assign fast_delivery if prep time < 20
        fast_delivery = preparation_time < 20

        # Newest: mark as newest if added today
        newest = True  # Default true when created; auto-remove later with cron/task

        # Create Item
        item = ItemTable.objects.create(
            name=name,
            category_id=category_id,
            subcategory_id=subcategory_id,
            subsubcategory_id=subsubcategory_id,
            is_veg=is_veg,
            description=description,
            price=price,
            preparation_time=preparation_time,
            inventory=inventory,
            calories=calories,
            fast_delivery=fast_delivery,
            newest=newest
        )

        # Assign Branches
        branch_ids = request.POST.getlist('branches')
        item.branches.set(branch_ids)

        # Images
        dish_images = request.FILES.getlist('dishImages[]')
        for img in dish_images:
            ItemImageTable.objects.create(item=item, image=img)

        # Voices
        voice_languages = request.POST.getlist('voiceLanguages[]')
        voice_files = request.FILES.getlist('voiceFiles[]')
        for lang, audio in zip(voice_languages, voice_files):
            VoiceDescriptionTable.objects.create(item=item, language=lang, audio_file=audio)

        # Variants
        index = 0
        while True:
            name_key = f"variants[{index}][name]"
            price_key = f"variants[{index}][price]"
            if name_key not in request.POST or price_key not in request.POST:
                break
            variant_name = request.POST[name_key]
            variant_price = request.POST[price_key]
            ItemVariantTable.objects.create(item=item, variant_name=variant_name, price=variant_price)
            index += 1

        # Addons
        addon_names = request.POST.getlist('addon_name[]')
        addon_prices = request.POST.getlist('addon_price[]')
        addon_images = request.FILES.getlist('addon_image[]')
        addon_descriptions = request.POST.getlist('addon_description[]')

        for name, price, desc, image in zip(addon_names, addon_prices, addon_descriptions, addon_images):
            AddonTable.objects.create(
                item=item,
                name=name,
                price=price or 0,
                description=desc,
                image=image
            )

        return redirect('view-dishes')
    

def get_subcategories(request):
    category_id = request.GET.get('category_id')
    if category_id:
        subcategories = SubCategoryTable.objects.filter(category_id=category_id).values('id', 'name')
        return JsonResponse(list(subcategories), safe=False)
    return JsonResponse([], safe=False)

def get_subsubcategories(request):
    subcategory_id = request.GET.get('subcategory_id')
    if subcategory_id:
        subsubcategories = SubSubCategoryTable.objects.filter(subcategory_id=subcategory_id).values('id', 'name')
        return JsonResponse(list(subsubcategories), safe=False)
    return JsonResponse([], safe=False)


class AddCarouselView(View):
    def get(self, request):
        c = OfferTable.objects.all()
        d = BranchTable.objects.all()
        return render(request, 'carouselAdd.html', {'offers': c, 'branches': d})

    def post(self, request):
        image = request.FILES.get('carouselImage')
        offer_id = request.POST.get('category')
        branch_ids = request.POST.getlist('branches[]')
        offer_percentage = request.POST.get('offerPercentage')
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')

        try:
            offer = OfferTable.objects.get(id=offer_id)
        except OfferTable.DoesNotExist:
            offer = None

        # Convert input date strings to datetime
        start_datetime = None
        end_datetime = None

        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
            except ValueError:
                start_datetime = None

        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
            except ValueError:
                end_datetime = None

        # Create carousel
        carousel = CarouselTable.objects.create(
            image=image,
            offer=offer,
            offer_percentage=offer_percentage if offer_percentage else 0.0,
            startdate=start_datetime,
            enddate=end_datetime
        )

        # Add branches
        if 'all' in branch_ids:
            branches = BranchTable.objects.all()
        else:
            branches = BranchTable.objects.filter(id__in=branch_ids)

        carousel.branch.set(branches)
        carousel.save()

        return redirect('view-carousel')


class EditDishView(View):
    def get(self, request):
        return render(request, 'dish_edit.html')


from django.utils.timezone import now, make_aware, is_naive


class AddOfferView(View):
    def get(self, request):
        c = ItemTable.objects.all()
        d = BranchTable.objects.all()
        return render(request, 'offerAdd.html', {'items': c, 'branches': d})

    def post(self, request):
        item_id = request.POST.get('itemid')
        name = request.POST.get('name')
        offer_percentage = request.POST.get('offer_percentage')
        offer_description = request.POST.get('offer_description')
        start_date_str = request.POST.get('startdate')
        end_date_str = request.POST.get('enddate')
        branch_id = request.POST.get('branch')

        if not branch_id:
            messages.error(request, "Please select a branch.")
            return redirect('add-offer')

        try:
            ist = pytz.timezone('Asia/Kolkata')

            start_datetime = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M') if start_date_str else None
            end_datetime = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M') if end_date_str else None

            if start_datetime and is_naive(start_datetime):
                start_datetime = ist.localize(start_datetime)
            if end_datetime and is_naive(end_datetime):
                end_datetime = ist.localize(end_datetime)

            current_time = datetime.now(pytz.utc).astimezone(ist)

            is_active = start_datetime <= current_time <= end_datetime if (start_datetime and end_datetime) else False

        except ValueError:
            messages.error(request, "Invalid date/time format.")
            return redirect('add-offer')

        try:
            item = ItemTable.objects.get(id=item_id)
            branch = BranchTable.objects.get(id=branch_id)

            OfferTable.objects.create(
                itemid=item,
                name=name,
                offer_percentage=offer_percentage,
                offerdescription=offer_description,
                startdate=start_datetime,
                enddate=end_datetime,
                branch=branch,
                is_active=is_active,
            )

            messages.success(request, "Offer added successfully.")
        except ItemTable.DoesNotExist:
            messages.error(request, "Invalid item selected.")
        except BranchTable.DoesNotExist:
            messages.error(request, "Invalid branch selected.")

        return redirect('view-offer')

    
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
            return redirect('registerstaff')

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
        return redirect('view-staff')

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
        carousels = CarouselTable.objects.all()
        current_time = now()
        print("Current Server Time (UTC or your TZ):", current_time)

        updated_carousels = []

        for carousel in carousels:
            print("Start:", carousel.startdate)
            print("End:", carousel.enddate)
 
            is_active = (
                carousel.startdate <= current_time <= carousel.enddate
                if carousel.startdate and carousel.enddate
                else False
            )

            branch_names = ", ".join(branch.name for branch in carousel.branch.all())

            carousel.start_ist = localtime(carousel.startdate).strftime('%d-%m-%Y %I:%M %p') if carousel.startdate else ""
            carousel.end_ist = localtime(carousel.enddate).strftime('%d-%m-%Y %I:%M %p') if carousel.enddate else ""
            carousel.is_active = is_active
            carousel.branch_names = branch_names

            updated_carousels.append(carousel)

        return render(request, 'viewcarousel.html', {'carousels': updated_carousels})
    
    
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

class DeleteOfferView(View):
    def get(self, request, id):
        c = OfferTable.objects.filter(id=id)
        c.delete()
        return redirect('view-offer')

from django.utils.timezone import make_aware

from django.utils.timezone import now
from django.utils.timezone import make_aware
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from Accountapp.models import OfferTable, ItemTable, BranchTable
from datetime import datetime
import pytz

class EditOfferView(View):
    def get(self, request, offer_id):
        offer = get_object_or_404(OfferTable, id=offer_id)
        items = ItemTable.objects.all()
        branches = BranchTable.objects.all()

        # Convert to naive IST for datetime-local input
        ist = pytz.timezone('Asia/Kolkata')
        if offer.startdate:
            offer.startdate = offer.startdate.astimezone(ist).replace(tzinfo=None)
        if offer.enddate:
            offer.enddate = offer.enddate.astimezone(ist).replace(tzinfo=None)

        return render(request, 'edit_offer.html', {
            'offer': offer,
            'items': items,
            'branches': branches,
        })

    def post(self, request, offer_id):
        offer = get_object_or_404(OfferTable, id=offer_id)
        ist = pytz.timezone('Asia/Kolkata')

        if 'name' in request.POST:
            offer.name = request.POST['name']

        if 'itemid' in request.POST and request.POST['itemid']:
            offer.itemid_id = request.POST['itemid']

        if 'offer_percentage' in request.POST:
            offer.offer_percentage = request.POST['offer_percentage']

        if 'offer_description' in request.POST:
            offer.offerdescription = request.POST['offer_description']

        if 'startdate' in request.POST:
            try:
                start_naive = datetime.strptime(request.POST['startdate'], '%Y-%m-%dT%H:%M')
                offer.startdate = ist.localize(start_naive)
            except ValueError:
                pass

        if 'enddate' in request.POST:
            try:
                end_naive = datetime.strptime(request.POST['enddate'], '%Y-%m-%dT%H:%M')
                offer.enddate = ist.localize(end_naive)
            except ValueError:
                pass

        if 'branch' in request.POST and request.POST['branch']:
            offer.branch_id = request.POST['branch']

        # Update is_active based on current IST time
        current_time_ist = now().astimezone(ist)
        offer.is_active = (
            offer.startdate and offer.enddate and
            offer.startdate <= current_time_ist <= offer.enddate
        )

        offer.save()
        return redirect('view-offer')


     

class ViewComplaintView(View):
    def get(self, request):
        return render(request, 'viewcomplaint.html')
    
class ViewDishesView(View):
    def get(self, request):
        items = ItemTable.objects.all()

        items_with_images = []
        for item in items:
            images = ItemImageTable.objects.filter(item=item)
            items_with_images.append({
                'item': item,
                'images': images
            })

        return render(request, 'viewdishes.html', {'items_with_images': items_with_images})
    
class DeleteDishes(View):
    def get(self, request, id):
        c=ItemTable.objects.get(id=id)
        c.delete()
        return redirect('view-dishes')
    
# class ViewOfferView(View):
#     def get(self, request):
#         return render(request, 'viewoffer.html')



from django.shortcuts import render
from django.views import View
from django.utils.timezone import now


class ViewOfferView(View):
    def get(self, request):
        utc_now = now()
        ist = pytz.timezone('Asia/Kolkata')
        current_time_ist = utc_now.astimezone(ist)

        offers = OfferTable.objects.select_related('itemid', 'branch').order_by('-startdate')

        for offer in offers:
            offer.product = offer.itemid.name if offer.itemid else "N/A"
            offer.title = offer.name
            offer.discount = offer.offer_percentage
            offer.start_date = offer.startdate.astimezone(ist) if offer.startdate else None
            offer.end_date = offer.enddate.astimezone(ist) if offer.enddate else None
            offer.branches = offer.branch.name if offer.branch else "All"

            # Use UTC time for DB logic, IST only for display
            new_status = (
                offer.startdate and offer.enddate and
                offer.startdate <= utc_now <= offer.enddate
            )

            if offer.is_active != new_status:
                offer.is_active = new_status
                offer.save(update_fields=['is_active'])

        return render(request, 'viewoffer.html', {'offers': offers})



    
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


from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages


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

        # Determine role from existing record
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
        return redirect('view-staff')


class EditDishView(View):
    def get(self, request, item_id):
        item = ItemTable.objects.get(id=item_id)
        categories = CategoryTable.objects.all()
        subcategories = SubCategoryTable.objects.filter(category=item.category)
        subsubcategories = SubSubCategoryTable.objects.filter(subcategory=item.subcategory)
        branches = BranchTable.objects.all()
        item_branches = list(item.branches.values_list('id', flat=True))
        variants = ItemVariantTable.objects.filter(item=item)
        voices = VoiceDescriptionTable.objects.filter(item=item)
        images = ItemImageTable.objects.filter(item=item)
        addons = AddonTable.objects.filter(item=item)
        print("Selected branches:", item.branches.values_list('id', flat=True))
        return render(request, 'edit_dish.html', {
                'item': item,
                'categories': categories,
                'subcategories': subcategories,
                'subsubcategories': subsubcategories,
                'branches': branches,
                'variants': variants,
                'voices': voices,
                'images': images,
                'addons': addons,
                'item_branches': item_branches  
            })


    def post(self, request, item_id):
        item = ItemTable.objects.get(id=item_id)

        # Basic fields
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.category_id = request.POST.get('category')
        item.subcategory_id = request.POST.get('subcategory')
        item.subsubcategory_id = request.POST.get('subsubcategory')
        item.calories = request.POST.get('calories')
        item.preparation_time = request.POST.get('preparation_time')
        item.is_veg = request.POST.get('is_veg') == 'True'

        # Price field
        try:
            item.price = float(request.POST.get('price') or 0)
        except (ValueError, TypeError):
            item.price = 0.0

        # Inventory field (handle blank/null values)
        inventory_val = request.POST.get('inventory')
        if inventory_val and inventory_val.isdigit():
            item.inventory = int(inventory_val)
        else:
            item.inventory = None  # or 0 if you prefer default

        item.save()

        # Variants
        ItemVariantTable.objects.filter(item=item).delete()
        variant_names = request.POST.getlist('variant_name[]')
        variant_prices = request.POST.getlist('variant_price[]')
        for index in range(len(variant_names)):
            ItemVariantTable.objects.create(
                item=item,
                name=variant_names[index],
                price=variant_prices[index]
            )

        # Images
        if request.FILES.getlist('dishImages[]'):
            ItemImageTable.objects.filter(item=item).delete()
            for img in request.FILES.getlist('dishImages[]'):
                ItemImageTable.objects.create(item=item, image=img)

        # Voice notes
        existing_voices = VoiceDescriptionTable.objects.filter(item=item)
        existing_voice_dict = {v.language: v for v in existing_voices}

        for i, audio in enumerate(request.FILES.getlist('voice_notes[]')):
            lang = request.POST.getlist('voice_languages[]')[i]
            if audio:
                if lang in existing_voice_dict:
                    existing_voice_dict[lang].delete()
                VoiceDescriptionTable.objects.create(item=item, voice_note=audio, language=lang)

        # Branches
        item.branches.set(request.POST.getlist('branches'))

        return redirect('view-dishes')


def search_dishes(request):
    query = request.GET.get('q', '')
    if query:
        matches = ItemTable.objects.filter(name__icontains=query).values('id', 'name')[:10]
        return JsonResponse(list(matches), safe=False)
    return JsonResponse([], safe=False)


class DeleteCarousel(View):
    def get(self, request, id):
        c = CarouselTable.objects.get(id=id)
        c.delete()
        return redirect('view-carousel')
    


# class EditCarousel(View):
#     def get(self, request, carousel_id):
#         carousel = get_object_or_404(CarouselTable, id=carousel_id)
#         offer = carousel.offer
#         items = ItemTable.objects.all()
#         branches = BranchTable.objects.all()

#         # Convert to local time (IST)
#         startdate = timezone.localtime(carousel.startdate) if carousel.startdate else None
#         enddate = timezone.localtime(carousel.enddate) if carousel.enddate else None

#         return render(request, 'editcarousel.html', {
#             'offer': offer,
#             'carousel': carousel,
#             'items': items,
#             'branches': branches,
#             'startdate': startdate.strftime('%Y-%m-%dT%H:%M') if startdate else '',
#             'enddate': enddate.strftime('%Y-%m-%dT%H:%M') if enddate else '',
#         })

#     def post(self, request, carousel_id):
#         carousel = get_object_or_404(CarouselTable, id=carousel_id)
#         offer = carousel.offer

#         # 1. Get form fields
#         name = request.POST.get('name')
#         offer_percentage = request.POST.get('offer_percentage')
#         offer_description = request.POST.get('offer_description')
#         itemid = request.POST.get('itemid')
#         branch_ids = request.POST.getlist('branch')
#         start_date = request.POST.get('startdate')
#         end_date = request.POST.get('enddate')

#         # 2. Convert input date strings to timezone-aware datetime (IST → UTC)
#         ist = pytz.timezone('Asia/Kolkata')
#         start_datetime = None
#         end_datetime = None

#         if start_date:
#             try:
#                 start_naive = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
#                 start_datetime = make_aware(start_naive, ist)
#             except ValueError:
#                 pass

#         if end_date:
#             try:
#                 end_naive = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
#                 end_datetime = make_aware(end_naive, ist)
#             except ValueError:
#                 pass

#         # 3. Update Offer
#         if offer:
#             offer.name = name
#             offer.offer_percentage = offer_percentage
#             offer.offerdescription = offer_description
#             offer.startdate = start_datetime
#             offer.enddate = end_datetime
#             offer.itemid_id = itemid
#             if branch_ids:
#                 offer.branch_id = branch_ids[0]  # assuming one branch
#             offer.save()

#         # 4. Update Carousel
#         carousel.offer_percentage = offer_percentage
#         carousel.startdate = start_datetime
#         carousel.enddate = end_datetime
#         if branch_ids:
#             carousel.branch.set(branch_ids)
#         if 'image' in request.FILES:
#             carousel.image = request.FILES['image']
#         carousel.save()

#         return redirect('view-carousel')

class ViewCouponView(View):
    def get(self, request):
        today = datetime.now().date()

        coupons = CouponTable.objects.all()

        for coupon in coupons:
            # Check if it's still active based on date range
            if coupon.valid_from and coupon.valid_to:
                try:
                    valid_from_date = datetime.strptime(coupon.valid_from, '%Y-%m-%d').date()
                    valid_to_date = datetime.strptime(coupon.valid_to, '%Y-%m-%d').date()
                    coupon.is_active = valid_from_date <= today <= valid_to_date
                except ValueError:
                    coupon.is_active = False

        return render(request, 'coupenview.html', {'coupons': coupons})
    
    

class AddCouponView(View):
    def get(self, request):
        return render(request, 'coupon.html')
    
    def post(self, request):
        try:
            code = request.POST.get('code')
            description = request.POST.get('description')
            discount_type = request.POST.get('discount_type')
            discount_percentage = request.POST.get('discount_percentage') if discount_type == 'percentage' else None
            max_discount_amount = request.POST.get('max_discount_amount') if discount_type == 'amount' else None
            min_order_amount = request.POST.get('min_order_amount')
            valid_from = request.POST.get('valid_from')
            valid_to = request.POST.get('valid_to')
            usage_limit = request.POST.get('usage_limit')

            # Parse valid_from and valid_to to date objects
            valid_from_date = datetime.strptime(valid_from, "%Y-%m-%d").date() if valid_from else None
            valid_to_date = datetime.strptime(valid_to, "%Y-%m-%d").date() if valid_to else None
            today = date.today()

            # Determine is_active
            is_active = False
            if valid_from_date and valid_to_date:
                is_active = valid_from_date <= today <= valid_to_date

            # Save the coupon
            coupon = CouponTable.objects.create(
                code=code,
                description=description,
                discount_percentage=discount_percentage or None,
                max_discount_amount=max_discount_amount or None,
                min_order_amount=min_order_amount,
                valid_from=valid_from,
                valid_to=valid_to,
                usage_limit=usage_limit,
                used_count='0',
                is_active=is_active
            )

            return redirect('view-coupon')

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

class EditCouponView(View):
    def get(self, request, coupon_id):
        coupon = get_object_or_404(CouponTable, id=coupon_id)
        return render(request, 'editcoupon.html', {'coupon': coupon})

    def post(self, request, coupon_id):
        coupon = get_object_or_404(CouponTable, id=coupon_id)

        coupon.code = request.POST.get('code')
        coupon.description = request.POST.get('description')
        coupon.discount_percentage = request.POST.get('discount_percentage') or None
        coupon.max_discount_amount = request.POST.get('max_discount_amount') or None
        coupon.min_order_amount = request.POST.get('min_order_amount') or None
        coupon.valid_from = request.POST.get('valid_from')
        coupon.valid_to = request.POST.get('valid_to')
        coupon.usage_limit = request.POST.get('usage_limit')

        # Ensure only one discount type is used
        discount_type = request.POST.get('discount_type')
        if discount_type == "percentage":
            coupon.max_discount_amount = None
        elif discount_type == "amount":
            coupon.discount_percentage = None

        coupon.save()
        return redirect('/view-coupon')  
    
class DeleteCouponView(View):
    def get(self, request, id):
        c = CouponTable.objects.get(id=id)
        c.delete()
        return redirect('view-coupon')