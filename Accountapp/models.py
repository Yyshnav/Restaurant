from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models

USER_TYPE_CHOICES = [
    ('ADMIN', 'Admin'),
    ('MANAGER', 'Manager'),
    ('KITCHEN', 'Kitchen'),
    ('WAITER', 'Waiter'),
    ('DELIVERY', 'Delivery Boy'),
    ('USER', 'User'),
]

class LoginTable(AbstractUser):
    # Add phone and role info
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.user_type == 'USER':
            self.username = self.phone  # username is still required, so use phone
            self.set_unusable_password()  # disable password for phone-login users
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_type} - {self.username or self.phone}"
    
class ProfileTable(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    image = models.FileField(upload_to='profile_images/', null=True, blank=True)
    dob = models.CharField(max_length=20, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    place = models.CharField(max_length=255, null=True, blank=True)
    loginid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='profile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
        
class CategoryTable(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class SubCategoryTable(models.Model):
    category = models.ForeignKey('CategoryTable', on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class ItemTable(models.Model):
    TYPE_CHOICES = [
        ('VEG', 'Vegetarian'),
        ('NONVEG', 'Non-Vegetarian'),
        ('BEVERAGE', 'Beverage'),
        ('DESSERT', 'Dessert'),
        ('ADDON', 'Addon'),
    ]

    name = models.CharField(max_length=100)
    category = models.ForeignKey('CategoryTable', on_delete=models.CASCADE, related_name='items')
    subcategory = models.ForeignKey('SubCategoryTable', on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    image = models.FileField(upload_to='item_images/', null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    voice_description = models.FileField(upload_to='voice_descriptions/', null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fast_delivery = models.BooleanField(default=False)
    newest = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name


class AddonTable(models.Model):
    item = models.ForeignKey(ItemTable, on_delete=models.CASCADE, related_name='addons')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='addon_images/', null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Addon for {self.item.name})"

            
class OfferTable(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    startdate = models.CharField(max_length=100, null=True, blank=True)
    enddate = models.CharField(max_length=100, null=True, blank=True)
    offer_percentage = models.FloatField(null=True, blank=True)
    itemid = models.ForeignKey(ItemTable, on_delete=models.CASCADE, related_name='offers')
    offerdescription = models.CharField(max_length=100, null=True, blank=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
# No, you do not need separate tables for service and dish ratings.
# Your current RatingTable is sufficient. It uses a 'rating_type' field to distinguish between service and dish ratings.
# This is a normalized and scalable approach.

class RatingTable(models.Model):
    RATING_TYPE_CHOICES = [
        ('SERVICE', 'Service'),
        ('DISH', 'Dish'),
    ]
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='ratings')
    itemid = models.ForeignKey(ItemTable, on_delete=models.CASCADE, related_name='ratings', null=True, blank=True)
    rating_type = models.CharField(max_length=10, choices=RATING_TYPE_CHOICES, null=True, blank=True)  # 'DISH' for food items, 'SERVICE' for delivery or service ratings
    rating = models.CharField(max_length=10,null=True, blank=True)
    comment = models.CharField(max_length=100, null=True, blank=True)  # Show textbox if rating == 1 in frontend
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)

    def __str__(self):
        target = self.itemid if self.rating_type == 'DISH' else self.userid
        return f"{self.userid} rated {target} ({self.rating_type}) - {self.rating}"
    
class CartTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='cart_items')
    fooditem = models.ForeignKey(ItemTable, on_delete=models.CASCADE, related_name='cart_entries')
    quantity = models.CharField(max_length=100, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)  # Price at the time item was added
    addon = models.ForeignKey(ItemTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_addons')
    instruction = models.CharField(max_length=200, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.FloatField(null=True, blank=True)  # Optional: price * quantity

    def __str__(self):
        return f"{self.userid} - {self.fooditem} x {self.quantity}"
    
class WishlistTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='wishlist_items')
    fooditem = models.ForeignKey(ItemTable, on_delete=models.CASCADE, related_name='wishlist_entries')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.userid} - {self.fooditem}"
    
class OrderTable(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PREPARING', 'Preparing'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='orders')
    totalamount = models.FloatField(null=True, blank=True)
    orderstatus = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    paymentstatus = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    deliveryid = models.ForeignKey(LoginTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.userid} - {self.orderstatus}"
    
class OrderItemTable(models.Model):
    order = models.ForeignKey(OrderTable, on_delete=models.CASCADE, related_name='order_items')
    itemname = models.ForeignKey(ItemTable, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    instruction = models.TextField(null=True, blank=True)
    addon = models.ForeignKey(ItemTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='addon_order_items')

    def __str__(self):
        return f"{self.order} - {self.itemname} x {self.quantity}"
    
class DeliveryTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='deliveries_info')
    name = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    phone = models.CharField(max_length=15)
    instruction = models.CharField(max_length=200, null=True, blank=True)  # Can store text or a reference to a voice file
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"
    
class ComplaintTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='complaints')
    deliveryid = models.ForeignKey(DeliveryTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    complaint = models.CharField(max_length=255, null=True, blank=True)
    image = models.FileField(upload_to='complaint_images/', null=True, blank=True)
    reply = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Complaint by {self.userid} (Delivery: {self.deliveryid})"
    
class DeliveryBoyTable(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    image = models.FileField(upload_to='deliveryboy_images/', null=True, blank=True)
    idproof = models.FileField(upload_to='deliveryboy_idproofs/', null=True, blank=True)
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='deliveryboy_profile')

    def __str__(self):
        return f"{self.name} ({self.phone})"

class PaymentTable(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
        ('WALLET', 'Wallet'),
        ('NETBANKING', 'Net Banking'),
    ]
    order = models.ForeignKey(OrderTable, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, default='PENDING')
    payment_date = models.DateTimeField(auto_now_add=True)
    details = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Payment {self.transaction_id} for Order #{self.order.id}"

class AddressTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.address_line1}, {self.city}"

# class TableBookingTable(models.Model):
#     userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='table_bookings')
#     name = models.CharField(max_length=100)
#     phone = models.CharField(max_length=15)
#     booking_date = models.DateField()
#     booking_time = models.TimeField()
#     number_of_people = models.CharField(max_length=100, null=True, blank=True)
#     special_request = models.TextField(null=True, blank=True)
#     status = models.CharField(max_length=20, choices=[
#         ('PENDING', 'Pending'),
#         ('CONFIRMED', 'Confirmed'),
#         ('CANCELLED', 'Cancelled'),
#         ('COMPLETED', 'Completed'),
#     ], default='PENDING')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Table Booking by {self.name} on {self.booking_date} at {self.booking_time}"

class CouponTable(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    discount_percentage = models.FloatField(null=True, blank=True)
    max_discount_amount = models.FloatField(null=True, blank=True)
    min_order_amount = models.FloatField(null=True, blank=True)
    valid_from = models.CharField(max_length=25, null=True, blank=True)
    valid_to = models.CharField(max_length=25, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    usage_limit = models.CharField(max_length=25, null=True, blank=True)
    used_count = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        return self.code

class FeedbackTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='feedbacks')
    feedback = models.TextField()
    rating = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.userid}"

class VoucherTable(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    value = models.FloatField(null=True, blank=True)
    valid_from = models.CharField(max_length=25, null=True, blank=True)
    valid_to = models.CharField(max_length=25, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    userid = models.ForeignKey(LoginTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='vouchers')
    used = models.BooleanField(default=False)
    used_at = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        return self.code
    
class KitchenSectionTable(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

class KitchenTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='kitchen_profile')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    image = models.ImageField(upload_to='kitchen_images/', null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    section = models.ForeignKey(KitchenSectionTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='kitchen_staff')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone}) - {self.section.name if self.section else 'No Section'}"

class ManagerTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='manager_profile')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    image = models.FileField(upload_to='manager_images/', null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    idproof = models.FileField(upload_to='manager_idproofs/', null=True, blank=True)
    qualification = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"

class WaiterTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='waiter_profile')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    image = models.FileField(upload_to='waiter_images/', null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    idproof = models.FileField(upload_to='waiter_idproofs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"

    # The current models cover most basic restaurant app needs: users, profiles, menu, cart, orders, delivery, complaints, ratings, wishlist, and offers.
    # Depending on your requirements, you might consider adding:
    #
    # 1. PaymentTable: To store payment transaction details (transaction id, payment method, etc.)
    # 2. AddressTable: To allow users to save multiple delivery addresses.
    # 3. NotificationTable: To manage notifications sent to users.
    # 4. TableBookingTable: If your restaurant supports table reservations.
    # 5. CouponTable: For promo codes and discounts not tied to specific items.
    # 6. FeedbackTable: For general feedback not related to orders or complaints.
    #
    # Add these only if your business logic requires them.
    
