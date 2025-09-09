import json
import uuid
import logging
from datetime import datetime
from decimal import Decimal
from django.shortcuts import redirect, render, HttpResponseRedirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.contrib.auth.views import LoginView, LogoutView
from django.utils import timezone
import pytz

from Accountapp.models import *

logger = logging.getLogger(__name__)

class WaiterView(View):
    def get(self, request):
        return render(request, 'waiter.html')
# views.py
from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from Accountapp.models import *
from django.utils.timezone import now, localtime

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render

@login_required(login_url='/')
@never_cache
def ordering(request):
    # Only allow access if session flag is set
    if not request.session.get('waiter_access', False):
        return redirect('/')  # redirect to manager login/dashboard

    # Clear session flag to prevent back navigation
    request.session['waiter_access'] = False

    # --- your existing code for items/tables/waiters ---
    if not ItemTable.objects.exists():
        category = CategoryTable.objects.get_or_create(name="food")[0]
        branch = BranchTable.objects.get_or_create(name="Main Branch")[0]
        DiningTable.objects.get_or_create(table_number="1", branch=branch)
        DiningTable.objects.get_or_create(table_number="2", branch=branch)
        WaiterTable.objects.get_or_create(
            name="Waiter1", userid=User.objects.get_or_create(username="waiter1")[0]
        )
        WaiterTable.objects.get_or_create(
            name="Waiter2", userid=User.objects.get_or_create(username="waiter2")[0]
        )
        item1 = ItemTable.objects.get_or_create(
            name="Burger", price=5.99, category=category,
            images=[{"url": "default.jpg"}]
        )[0]
        item2 = ItemTable.objects.get_or_create(
            name="Pizza", price=8.99, category=category,
            images=[{"url": "default.jpg"}]
        )[0]
        ItemVariantTable.objects.get_or_create(item=item1, variant_name="Small", price=4.99)
        ItemVariantTable.objects.get_or_create(item=item1, variant_name="Large", price=7.99)
        ItemVariantTable.objects.get_or_create(item=item2, variant_name="Medium", price=6.99)
        ItemVariantTable.objects.get_or_create(item=item2, variant_name="Large", price=9.99)

    items = ItemTable.objects.all().prefetch_related('variants')
    tables = DiningTable.objects.all()
    waiters = WaiterTable.objects.all()
    branch = BranchTable.objects.first()

    items_with_variants = []
    for item in items:
        variants = list(item.variants.values('variant_name', 'price'))
        items_with_variants.append({
            'id': item.id,
            'name': item.name,
            'price': float(item.price),
            'category': item.category.name if item.category else 'uncategorized',
            'images': item.images,
            'variants': variants if variants else [{'variant_name': 'Standard', 'price': float(item.price)}]
        })

    context = {
        'items': items_with_variants,
        'tables': tables,
        'waiters': waiters,
        'branch': branch,
    }
    return render(request, 'waiter.html', context)



@csrf_exempt
def authenticate_waiter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        waiter_id = data.get('waiter_id')
        password = data.get('password')
        try:
            waiter = WaiterTable.objects.get(id=waiter_id)
            user = waiter.userid
            if user.check_password(password):
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Incorrect password'})
        except WaiterTable.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Waiter not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@csrf_exempt
def place_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        items_data = data.get('items', [])
        total = Decimal(data.get('total', '0'))
        selected_tables = data.get('selected_tables', [])
        waiter_id = data.get('waiter_id')

        if not items_data or not waiter_id:
            return JsonResponse({'success': False, 'message': 'Invalid data'}, status=400)

        try:
            branch = BranchTable.objects.first()
            waiter = WaiterTable.objects.get(id=waiter_id)

            order = OrderTable.objects.create(
                userid=None,
                branch=branch,
                subtotal=Decimal('0'),
                tax=Decimal('0'),
                discount=Decimal('0'),
                totalamount=Decimal('0'),
                paymentstatus='PENDING',
                orderstatus='ACCEPTED',
                payment_method='CASH',
            )

            subtotal = Decimal('0')
            for it in items_data:
                item_name = it.get('name')
                quantity = int(it.get('quantity', 1))
                instruction = it.get('note', '')
                variant_name = it.get('variant', 'Standard')  # Changed from 'portion' to 'variant'

                try:
                    item = ItemTable.objects.get(name=item_name)
                    variant = None
                    unit_price = Decimal(item.price)
                    if variant_name != 'Standard':
                        variant = ItemVariantTable.objects.get(item=item, variant_name=variant_name)
                        unit_price = Decimal(variant.price)
                    item_total = unit_price * quantity
                    subtotal += item_total

                    OrderItemTable.objects.create(
                        order=order,
                        itemname=item,
                        quantity=str(quantity),
                        price=unit_price,
                        instruction=instruction,
                        variant=variant,
                    )
                except (ItemTable.DoesNotExist, ItemVariantTable.DoesNotExist):
                    order.delete()
                    return JsonResponse({'success': False, 'message': 'Invalid item or variant'}, status=400)

            order.subtotal = subtotal
            order.totalamount = subtotal
            order.save()

            table = None
            if selected_tables:
                table_number = selected_tables[0]
                try:
                    table = DiningTable.objects.get(table_number=table_number, branch=branch)
                except DiningTable.DoesNotExist:
                    pass

            bill_number = 'BILL-' + str(order.id) + '-' + localtime(now()).strftime('%Y%m%d%H%M%S')
            BillTable.objects.create(
                order=order,
                branch=branch,
                table=table,
                waiter=waiter,
                bill_number=bill_number,
                subtotal=order.subtotal,
                tax=order.tax,
                discount=order.discount,
                total_amount=order.totalamount,
                status='PENDING',
                payment_method='COD',
                payment_channel='BY_HAND',
            )

            return JsonResponse({'success': True, 'message': 'Order placed successfully!'})
        except WaiterTable.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid waiter'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)