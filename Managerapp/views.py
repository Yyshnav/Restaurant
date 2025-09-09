from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from Accountapp.models import *
from django.views.decorators.cache import never_cache
from django.db.models import Min
from django.utils.decorators import method_decorator


# Create your views here.

@method_decorator(never_cache, name='dispatch')
class ManagerDash(LoginRequiredMixin, View):
    login_url = '/'  
    redirect_field_name = None  

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/')
        if request.user.user_roles.filter(role='MANAGER').exists():
            return render(request, 'dashboard.html')
        return redirect('/')




class CrediUser(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.GET.get("format") == "json":
            credit_users = list(CreditUser.objects.values())
            return JsonResponse({"credit_users": credit_users}, safe=False)

        return render(request, 'crediusers.html', {"credit_users": CreditUser.objects.all()})

    def post(self, request):
        Name = request.POST.get("Name")   
        Email = request.POST.get("Email") 
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        credit_limit = request.POST.get("credit_limit")

        CreditUser.objects.create(
            Name=Name,
            Email=Email,
            phone=phone,
            address=address,
            credit_limit=credit_limit
        )

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"message": "Credit User added successfully!"})

        messages.success(request, "Credit User added successfully!")
        return redirect("crediusers")



class DishesView(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        
        dishes = ItemTable.objects.prefetch_related('variants').all()
        return render(request, 'dishes.html', {"dishes": dishes})
    

def edit_variant_price(request, variant_id):
    variant = get_object_or_404(ItemVariantTable, id=variant_id)

    if request.method == "POST":
        new_price = request.POST.get("price")

        if new_price:
            variant.price = float(new_price)
            variant.save()

            # Update the related item with the lowest variant price
            item = variant.item
            lowest_price = item.variants.aggregate(Min('price'))['price__min']
            item.price = lowest_price
            item.save()

            return JsonResponse({
                "success": True,
                "message": "Variant price updated successfully",
                "new_price": variant.price,
                "item_price": item.price
            })

    return JsonResponse({"success": False, "message": "Invalid request"})



    
class OnlineOrdersView(View):
    def get(self, request):
        return render(request, 'onlineOrders.html')
    
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import JsonResponse
from django.shortcuts import render
from django.db import IntegrityError
import json


@method_decorator(ensure_csrf_cookie, name='dispatch')
class PrinterView(View):
    def get(self, request):
        # You can drop categories if you’re no longer showing them
        categories = CategoryTable.objects.prefetch_related('subcategories').all()
        printers = PrinterTable.objects.select_related('branch', 'subcategories').all()
        branches = BranchTable.objects.all()
        subcategories = SubCategoryTable.objects.all()

        return render(request, 'printer.html', {
            'categories': categories,
            'printers': printers,
            'branches': branches,
            'subcategories': subcategories,
        })

@csrf_exempt
def toggle_availability(request, pk):
    if request.method == "POST":
        dish = get_object_or_404(ItemTable, pk=pk)
        dish.available = not dish.available   # flip availability
        dish.save()
        return JsonResponse({"success": True, "available": dish.available})
    return JsonResponse({"success": False}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class AddPrinterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        name = data.get('name')
        branch_id = data.get('branch_id')
        sub_id = data.get('sub_id')
        ip_address = data.get('ip_address')  # optional

        if not all([name, branch_id, sub_id]):
            return JsonResponse({'error': 'name, branch_id and sub_id are required'}, status=400)

        # validate foreign keys
        branch = get_object_or_404(BranchTable, id=branch_id)
        sub = get_object_or_404(SubCategoryTable, id=sub_id)

        try:
            printer = PrinterTable.objects.create(
                name=name,
                branch=branch,
                subcategories=sub,   # if ManyToMany, do printer.subcategories.add(sub)
                ip_address=ip_address or None,
            )
        except IntegrityError:
            return JsonResponse({'error': 'Printer with this name already exists'}, status=400)

        messages.success(request, "Printer added successfully!")
        return JsonResponse({'reload': True}, status=201)

def edit_printer(request, pk):
    printer = get_object_or_404(PrinterTable, pk=pk)

    if request.method == "POST":
        try:
            printer.name = request.POST.get("name")
            printer.ip_address = request.POST.get("ip_address", "")

            branch_id = request.POST.get("branch_id")
            if branch_id:
                printer.branch = get_object_or_404(BranchTable, pk=branch_id)

            sub_id = request.POST.get("sub_id")
            if sub_id:
                subcategory = get_object_or_404(SubCategoryTable, pk=sub_id)
                printer.subcategories = subcategory   

            printer.save()

            return JsonResponse({
                "status": "success",
                "id": printer.id,
                "name": printer.name,
                "ip_address": printer.ip_address,
                "branch": printer.branch.name if printer.branch else None,
                "sub_id": sub_id,
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

    
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def delete_printer(request, pk):
    printer = get_object_or_404(PrinterTable, pk=pk)
    printer.delete()
    messages.success(request, "Printer deleted successfully!")
    return redirect('printer')  



class AddTableView(View):
    def get(self, request):
        tables = DiningTable.objects.all()  
        return render(request, 'table.html', {"tables": tables})


class SaveTableView(View):
    def post(self, request):
        user = request.user

        # Get manager profile to find branch
        try:
            manager = ManagerTable.objects.get(userid=user)
            branch = manager.BranchID
        except ManagerTable.DoesNotExist:
            return JsonResponse({"error": "Manager profile not found"}, status=400)

        floor = request.POST.get("floor")
        table_number = request.POST.get("table_number")
        seating_capacity = request.POST.get("seating_capacity")

        try:
            dining_table = DiningTable.objects.create(
                branch=branch,
                floor=floor,
                table_number=table_number,
                seating_capacity=seating_capacity,
            )
            return JsonResponse({
                "success": True,
                "id": dining_table.id,
                "floor": dining_table.floor,
                "table_number": dining_table.table_number,
                "seating_capacity": dining_table.seating_capacity
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


    
class TakeOrdersView(View):
    def get(self, request):
        if request.GET.get('format') == 'json':
            items = ItemTable.objects.prefetch_related("images", "variants").all()
            dishes = []

            for item in items:
                image_url = item.images.first().image.url if item.images.exists() else "https://via.placeholder.com/160"
                variants = [
                    {
                        "id": v.id,                         # ✅ send id
                        "name": v.variant_name,
                        "price": float(v.price)
                    }
                    for v in item.variants.all()
                ]

                dishes.append({
                    "id": item.id,
                    "name": item.name,
                    "price": float(item.price) if item.price else 0,
                    "category": item.category.name if item.category else "",
                    "image": image_url,
                    "variants": variants
                })

            waiters = list(WaiterTable.objects.values("id", "name"))
            tables = list(DiningTable.objects.values("id", "table_number", "floor", "seating_capacity", "is_available"))
            delivery_boys = list(DeliveryBoyTable.objects.values("id", "name"))

            return JsonResponse({
                "dishes": dishes,
                "waiters": waiters,
                "tables": tables,
                "delivery_boys": delivery_boys,
            })

        # Normal HTML render
        waiters = WaiterTable.objects.all()
        tables = DiningTable.objects.all()
        delivery_boys = DeliveryBoyTable.objects.all()
        return render(request, "take-order.html", {
            "waiters": waiters,
            "tables": tables,
            "delivery_boys": delivery_boys
        })


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from django.db import transaction



# @csrf_exempt
# def save_order(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid request method"}, status=405)

#     try:
#         data = json.loads(request.body.decode("utf-8"))
#         order_type = data.get("orderType")

#         # ✅ Map frontend → DB values
#         order_type_map = {
#             "dining": "DINE_IN",
#             "takeaway": "TAKEAWAY",
#             "online": "ONLINEDELIVERY",
#         }
#         if order_type not in order_type_map:
#             return JsonResponse({"error": "Invalid order type"}, status=400)

#         db_order_type = order_type_map[order_type]

#         # Dining-specific fields
#         table_id = data.get("tableId") if order_type == "dining" else None
#         waiter_id = data.get("waiterId") if order_type == "dining" else None
#         table = DiningTable.objects.get(id=table_id) if table_id else None
#         waiter = WaiterTable.objects.get(id=waiter_id) if waiter_id else None

#         # Takeaway / Online
#         customer_name = data.get("customerName") if order_type in ["takeaway", "online"] else None
#         customer_phone = data.get("customerPhone") if order_type in ["takeaway", "online"] else None

#         # Online delivery
#         deliveryboy = None
#         if order_type == "online":
#             deliveryboy_id = data.get("deliveryboyId")
#             if deliveryboy_id:
#                 deliveryboy = DeliveryBoyTable.objects.get(id=deliveryboy_id)

#         # ✅ Create Order
#         order = OfflineOrders.objects.create(
#             order_type=db_order_type,
#             table=table,
#             waiter=waiter,
#             customer_name=customer_name,
#             phone=customer_phone,
#             deliveryboy=deliveryboy,
#             total_amount=data.get("total", 0),
#         )

#         # ✅ Create Order Items
#         for item_data in data.get("items", []):
#             item = ItemTable.objects.get(id=item_data["itemId"])
#             variant = None
#             if item_data.get("variantId"):
#                 variant = ItemVariantTable.objects.get(id=item_data["variantId"])

#             OfflineOrderItems.objects.create(
#                 order=order,
#                 item=item,
#                 variant=variant,
#                 quantity=item_data.get("qty", 1),
#                 price=item_data.get("price", 0),
#                 note=item_data.get("note", "")
#             )

#         return JsonResponse({"success": True, "orderId": order.id})

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def save_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        order_type = data.get("orderType")

        order_type_map = {
            "dining": "DINE_IN",
            "takeaway": "TAKEAWAY",
            "online": "ONLINEDELIVERY",
        }
        if order_type not in order_type_map:
            return JsonResponse({"error": "Invalid order type"}, status=400)

        db_order_type = order_type_map[order_type]

        table_id = data.get("tableId") if order_type == "dining" else None
        waiter_id = data.get("waiterId") if order_type == "dining" else None
        table = DiningTable.objects.get(id=table_id) if table_id else None
        waiter = WaiterTable.objects.get(id=waiter_id) if waiter_id else None

        customer_name = data.get("customerName") if order_type in ["takeaway", "online"] else None
        customer_phone = data.get("customerPhone") if order_type in ["takeaway", "online"] else None

        deliveryboy = None
        if order_type == "online":
            deliveryboy_id = data.get("deliveryboyId")
            if deliveryboy_id:
                deliveryboy = DeliveryBoyTable.objects.get(id=deliveryboy_id)

        order = OfflineOrders.objects.create(
            order_type=db_order_type,
            table=table,
            waiter=waiter,
            customer_name=customer_name,
            phone=customer_phone,
            deliveryboy=deliveryboy,
            total_amount=data.get("total", 0),
        )

        for item_data in data.get("items", []):
            item = ItemTable.objects.get(id=item_data["itemId"])
            variant = None
            if item_data.get("variantId"):
                variant = ItemVariantTable.objects.get(id=item_data["variantId"])

            OfflineOrderItems.objects.create(
                order=order,
                item=item,
                variant=variant,
                quantity=item_data.get("qty", 1),
                price=item_data.get("price", 0),
                note=item_data.get("note", "")
            )

        return JsonResponse({"success": True, "orderId": order.id})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

from django.utils.dateformat import DateFormat
from django.utils.formats import get_format

from django.shortcuts import redirect

def go_to_waiter(request):
    # Allow Waiter access in session
    request.session['waiter_access'] = True
    return redirect('waiterdashboard')


    
class OrdersListView(View):
    def get(self, request):
        delivery_boys = DeliveryBoyTable.objects.all()
        if request.GET.get("format") == "json":
            orders = []

            for o in OfflineOrders.objects.select_related("table", "waiter", "deliveryboy"):
                orders.append({
                    "id": o.id,
                    "customer": o.customer_name or (o.table and f"Table {o.table.table_number}") or "Guest",
                    "platform": (
                        "Dining" if o.order_type == "DINE_IN" else
                        "Takeaway" if o.order_type == "TAKEAWAY" else
                        "Online"
                    ),
                    "total": float(o.total_amount or 0),
                    "status": "accepted" if o.status else "completed", 
                    "paymentStatus": o.payment.paymentstatus if o.payment else "Unpaid",
                    "date": DateFormat(o.created_at).format(get_format("DATE_FORMAT")),
                    "address": "",
                    "items": [
                        {
                            "name": item.item.name,
                            "quantity": item.quantity,
                            "price": str(item.price)
                        }
                        for item in o.order_items.all()
                    ],
                    "rejectReason": "",
                    "deliveryBoy": o.deliveryboy.name if o.deliveryboy else ""
                })


          
            for o in OrderTable.objects.select_related("userid", "deliveryid", "coupon"):
                    orders.append({
                        "id": o.id,
                        "customer": str(o.userid) if o.userid else "App User",
                        "platform": "Appthrough",
                        "total": float(o.totalamount or 0),
                        "status": o.orderstatus.lower(),  
                        "paymentStatus": o.paymentstatus.title(),
                        "date": DateFormat(o.created_at).format(get_format("DATE_FORMAT")),
                        "address": str(o.address) if o.address else "",
                        "items": [
                            {
                                "name": i.itemname.name,
                                "quantity": i.quantity,
                                "price": str(i.price)
                            }
                            for i in getattr(o, "order_item", []).all()
                        ] if hasattr(o, "order_item") else [],
                        "rejectReason": "",
                        "deliveryBoy": o.deliveryid.name if o.deliveryid else ""
                    })

            return JsonResponse({"orders": orders}, safe=False)

        
        return render(request, "view-orders.html", {"delivery_boys": delivery_boys})
    
class AcceptOrderView(View):
    def post(self, request, order_id):
        print("AcceptOrderView called")
        try:
            order = OrderTable.objects.get(id=order_id)
        except OrderTable.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)

        if order.orderstatus != 'PENDING':
            return JsonResponse({"error": "Only pending orders can be accepted"}, status=400)

        # Update status
        order.orderstatus = 'ACCEPTED'  # ✅ must match choices
        order.save(update_fields=["orderstatus"])
        return JsonResponse({"success": True, "message": f"Order #{order_id} accepted"})



class ViewStaff(View):
    def get(self, request):
        # Fetch all staff
        delivery_boys = DeliveryBoyTable.objects.all()
        waiters = WaiterTable.objects.all()
        managers = ManagerTable.objects.all()

        # Combine them into one list of dicts for the template
        staff_data = []

        for db in delivery_boys:
            staff_data.append({
                "id": f"DB{db.id}",
                "name": db.name,
                "role": "Delivery Boy",
                "status": "Active",  
                "status_class": "success",
                "join_date": "-",  
            })

        for w in waiters:
            staff_data.append({
                "id": f"W{w.id}",
                "name": w.name,
                "role": "Waiter",
                "status": "Active",
                "status_class": "success",
                "join_date": w.created_at.strftime("%Y-%m-%d") if w.created_at else "-",
            })

        for m in managers:
            staff_data.append({
                "id": f"M{m.id}",
                "name": m.name,
                "role": "Manager",
                "status": "Active",
                "status_class": "success",
                "join_date": m.created_at.strftime("%Y-%m-%d") if m.created_at else "-",
            })

        return render(request, "viewstaffman.html", {"staff_data": staff_data})
    

class StaffDetailView(View):
    def get(self, request, staff_id):
        prefix = staff_id[:2]   
        real_id = int(staff_id[2:])  

        staff_data = {}

        if prefix == "DB":  
            try:
                staff = DeliveryBoyTable.objects.get(id=real_id)
                staff_data = {
                    "id": f"DB{staff.id}",
                    "name": staff.name,
                    "role": "Delivery Boy",
                    "status": "Active",
                    "join_date": "-",  # no created_at field in your model
                    "phone": staff.phone,
                    "email": staff.email,
                    "address": staff.address,
                    "qualification": "-",  # not in model
                }
            except DeliveryBoyTable.DoesNotExist:
                return JsonResponse({"error": "Staff not found"}, status=404)

        elif prefix == "W":  # Waiter
            try:
                staff = WaiterTable.objects.get(id=real_id)
                staff_data = {
                    "id": f"W{staff.id}",
                    "name": staff.name,
                    "role": "Waiter",
                    "status": "Active",
                    "join_date": staff.created_at.strftime("%Y-%m-%d") if getattr(staff, "created_at", None) else "-",
                    "phone": getattr(staff, "phone", "-"),
                    "email": getattr(staff, "email", "-"),
                    "address": getattr(staff, "address", "-"),
                    "qualification": getattr(staff, "qualification", "-"),
                }
            except WaiterTable.DoesNotExist:
                return JsonResponse({"error": "Staff not found"}, status=404)

        elif prefix == "M":  # Manager
            try:
                staff = ManagerTable.objects.get(id=real_id)
                staff_data = {
                    "id": f"M{staff.id}",
                    "name": staff.name,
                    "role": "Manager",
                    "status": "Active",
                    "join_date": staff.created_at.strftime("%Y-%m-%d") if getattr(staff, "created_at", None) else "-",
                    "phone": getattr(staff, "phone", "-"),
                    "email": getattr(staff, "email", "-"),
                    "address": getattr(staff, "address", "-"),
                    "qualification": getattr(staff, "qualification", "-"),
                }
            except ManagerTable.DoesNotExist:
                return JsonResponse({"error": "Staff not found"}, status=404)

        return JsonResponse(staff_data)


class DeleteTableView(View):
    def post(self, request, table_id):
        try:
            table = DiningTable.objects.get(id=table_id)
            table.delete()
            return JsonResponse({"success": True})
        except DiningTable.DoesNotExist:
            return JsonResponse({"error": "Table not found"}, status=404)
        

class AssignDeliveryBoyView(View):
    def post(self, request, order_id):
        print("AssignDeliveryBoyView called")
        delivery_boy_id = request.POST.get("delivery_boy_id") or request.POST.get("deliveryBoyId")
        try:
            order = OrderTable.objects.get(id=order_id)
            delivery_boy = DeliveryBoyTable.objects.get(id=delivery_boy_id)
        except (OrderTable.DoesNotExist, DeliveryBoyTable.DoesNotExist):
            return JsonResponse({"error": "Order or Delivery Boy not found"}, status=404)

        order.deliveryid = delivery_boy
        order.orderstatus = "ASSIGNED"
        order.save(update_fields=["deliveryid", "orderstatus"])

        return JsonResponse({
            "success": True,
            "message": f"Order #{order_id} assigned to Delivery Boy {delivery_boy.name}"
        })



class RejectOrderView(View):
    def post(self, request, order_id):
        try:
            order = OrderTable.objects.get(id=order_id)
        except OrderTable.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)

        if order.orderstatus != 'PENDING':
            return JsonResponse({"error": "Only pending orders can be rejected"}, status=400)

        reason = request.POST.get("reason", "")

        # Update status
        order.orderstatus = 'REJECTED'
        order.delivery_instructions = f"Rejected: {reason}"  # or create a dedicated field
        order.save(update_fields=["orderstatus", "delivery_instructions"])

        return JsonResponse({"success": True, "message": f"Order #{order_id} rejected"})
    

class CreditUserListView(View):
    def get(self, request):
        users = list(CreditUser.objects.values("id", "Name"))
        return JsonResponse({"credit_users": users})
