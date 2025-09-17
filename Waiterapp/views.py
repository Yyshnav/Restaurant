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

from Accountapp.models import *

logger = logging.getLogger(__name__)

class WaiterView(View):
    def get(self, request):
        return render(request, 'waiter.html')
# views.py


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
        print(variants)

    context = {
        'items': items_with_variants,
        'tables': tables,
        'waiters': waiters,
        'branch': branch,
    }
    return render(request, 'waiter.html', context)

from django.views.decorators.http import require_GET


@require_GET
@csrf_exempt  # Temporarily disable CSRF for testing
@csrf_exempt
def get_variants(request, item_id):
    print("------------------innnn----->")
    try:
        print(f"Fetching variants for item ID:----------------------- {item_id}")
        
        variants = ItemVariantTable.objects.filter(item_id=item_id)
        print(f"Found {variants.count()} variants")
        
        variants_data = []
        for variant in variants:
            variants_data.append({
                'id': variant.id,
                'variant_name': variant.variant_name,
                'price': float(variant.price)
            })
        
        print(f"Returning data--------------: {variants_data}")
        return JsonResponse(variants_data, safe=False)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
        
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug print
        return JsonResponse({'error': str(e)}, status=500)



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
            # Get waiter and branch
            waiter = WaiterTable.objects.get(id=waiter_id)
            branch = BranchTable.objects.first()  # Or get branch from request/session
            
            # Get table if selected
            table = None
            if selected_tables:
                table_number = selected_tables[0]
                try:
                    table = DiningTable.objects.get(table_number=table_number, branch=branch)
                except DiningTable.DoesNotExist:
                    pass

            # Create OfflineOrders instance
            offline_order = OfflineOrders.objects.create(
                order_type='DINE_IN',  # Default to Dine In
                table=table,
                waiter=waiter,
                total_amount=total,
                payment='PENDING'  # Default payment status
            )

            # Create OfflineOrderItems for each item
            for item_data in items_data:
                item_name = item_data.get('name')
                quantity = int(item_data.get('quantity', 1))
                note = item_data.get('note', '')
                variant_name = item_data.get('variant', 'Standard')
                price = Decimal(item_data.get('price', '0'))

                try:
                    # Get the item
                    item = ItemTable.objects.get(name=item_name)
                    
                    # Get variant if specified
                    variant = None
                    if variant_name != 'Standard':
                        variant = ItemVariantTable.objects.get(
                            item=item, 
                            variant_name=variant_name
                        )
                    
                    # Create order item
                    OfflineOrderItems.objects.create(
                        order=offline_order,
                        item=item,
                        variant=variant,
                        quantity=quantity,
                        price=price,
                        note=note
                    )
                    
                except ItemTable.DoesNotExist:
                    offline_order.delete()
                    return JsonResponse({
                        'success': False, 
                        'message': f'Item "{item_name}" does not exist'
                    }, status=400)
                except ItemVariantTable.DoesNotExist:
                    offline_order.delete()
                    return JsonResponse({
                        'success': False, 
                        'message': f'Variant "{variant_name}" for item "{item_name}" does not exist'
                    }, status=400)

            return JsonResponse({
                'success': True, 
                'message': 'Order placed successfully!',
                'order_id': offline_order.id
            })
            
        except WaiterTable.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid waiter'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)