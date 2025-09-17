from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.timezone import now, localtime

from rest_framework.views import APIView


# ------------------------
# UserRole Model
# ------------------------
class UserRole(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('KITCHEN', 'Kitchen'),
        ('WAITER', 'Waiter'),
        ('DELIVERY', 'Delivery Boy'),   
        ('USER', 'User'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.role

# ------------------------
# LoginTable Model
# ------------------------
class LoginTable(AbstractUser):
    notification_token = models.CharField(max_length=455, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    user_roles = models.ManyToManyField(UserRole, related_name='users',)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Set username to phone if not already set
        if not self.username and self.phone:
            self.username = self.phone
            self.set_unusable_password()
        super().save(*args, **kwargs)

    def __str__(self):
        # Safely list all assigned roles
        roles = ', '.join([role.role for role in self.user_roles.all()])
        return f"{roles} - {self.username or self.phone}"
    
class BranchTable(models.Model):
    name = models.CharField(max_length=100, unique=True)
    place = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='branch_image/', null=True, blank=True)
    address = models.CharField(max_length=255)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    floors = models.IntegerField(null=True, blank=True) 
    fssai_lic_no = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class AddressTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, blank=True, null=True)  # Added userid
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=455, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.address}, {self.city}"
    
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
    
class DeliveryBoyTable(models.Model):
    name = models.CharField(max_length=400)
    phone = models.CharField(max_length=15)
    email = models.CharField(max_length=100, null=True, blank=True)
    branch = models.ForeignKey(BranchTable, on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=255)
    image = models.FileField(upload_to='deliveryboy_images/', null=True, blank=True)
    idproof = models.FileField(upload_to='deliveryboy_idproofs/', null=True, blank=True)
    license = models.FileField(upload_to='deliveryboy_licenses/', null=True, blank=True)
    userid = models.OneToOneField(LoginTable, on_delete=models.CASCADE, related_name='deliveryboy_profile')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        """Whenever we create a DeliveryBoy, make sure user has DELIVERY role."""
        super().save(*args, **kwargs)
        delivery_role, _ = UserRole.objects.get_or_create(role="DELIVERY")
        self.userid.user_roles.add(delivery_role)
        self.userid.save()

    def __str__(self):
        return f"{self.name} ({self.phone})"
    
class ProfileTable(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    image = models.FileField(upload_to='profile_images/', null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    dob = models.CharField(max_length=20, null=True, blank=True)
    # latitude = models.FloatField(null=True, blank=True)
    # longitude = models.FloatField(null=True, blank=True)
    # place = models.CharField(max_length=255, null=True, blank=True)
    address = models.ForeignKey(AddressTable, on_delete=models.SET_NULL, related_name='deliverie', null=True, blank=True)
    loginid = models.OneToOneField(LoginTable, on_delete=models.CASCADE, related_name='profile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class DeliveryBoyLocation(models.Model):
    delivery_boy = models.OneToOneField(DeliveryBoyTable, on_delete=models.CASCADE, related_name='location')
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.delivery_boy.name} - Lat: {self.latitude}, Long: {self.longitude}"
    
class ProfileTable(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    image = models.FileField(upload_to='profile_images/', null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    dob = models.CharField(max_length=20, null=True, blank=True)
    # latitude = models.FloatField(null=True, blank=True)
    # longitude = models.FloatField(null=True, blank=True)
    # place = models.CharField(max_length=255, null=True, blank=True)
    address = models.ForeignKey(AddressTable, on_delete=models.SET_NULL, related_name='deliverie', null=True, blank=True)
    loginid = models.OneToOneField(LoginTable, on_delete=models.CASCADE, related_name='profile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):  
        return self.name

    
class OrderTable(models.Model):
    userid = models.ForeignKey(ProfileTable, on_delete=models.CASCADE, blank=True, null=True)
    branch = models.ForeignKey(BranchTable, on_delete=models.CASCADE, blank=True, null=True)
    coupon = models.ForeignKey(CouponTable, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.ForeignKey(AddressTable, on_delete=models.SET_NULL, null=True, blank=True)
    deliveryid = models.ForeignKey(DeliveryBoyTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    totalamount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    paymentstatus = models.CharField(max_length=50, choices=[
        ("PENDING", "Pending"), ("PAID", "Paid"), ("FAILED", "Failed")
    ], default="PENDING")

    orderstatus = models.CharField(max_length=50, choices=[
        ("PENDING", "Pending"), ("ACCEPTED", "Accepted"), ("REJECTED", "Rejected"),
        ("CANCELLED", "Cancelled"), ("DELIVERED", "Delivered"),("PICKED", "Picked"), ('ASSIGNED', "Assigned")
    ], default="PENDING")

    cooking_instructions = models.TextField(blank=True, null=True)
    delivery_instructions = models.TextField(blank=True, null=True)
    voice_instruction = models.FileField(upload_to='order_voice_instructions/', null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_totals(self):
        # Ensure all arithmetic uses Decimal
        subtotal = sum(
            item.price * Decimal(item.quantity)
            for item in self.order_item.all()
            if item.quantity and item.quantity.strip().isdigit()
        )
        self.subtotal = subtotal
        self.tax = subtotal * Decimal('0.05')  # 5% tax as Decimal
        self.discount = self.coupon.discount_amount if self.coupon else Decimal('0')
        self.totalamount = self.subtotal + self.tax - self.discount
        self.save()

    def __str__(self):
        return f"Order #{self.id} by {self.userid}"


        
class CategoryTable(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class SubCategoryTable(models.Model):
    category = models.ForeignKey(CategoryTable, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='subcategory_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
class SubSubCategoryTable(models.Model):
    subcategory = models.ForeignKey(SubCategoryTable, on_delete=models.CASCADE, related_name='subsubcategories')
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='subsubcategory_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subcategory.category.name} > {self.subcategory.name} > {self.name}"


class ItemTable(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(CategoryTable, on_delete=models.CASCADE, related_name='items')
    subcategory = models.ForeignKey(SubCategoryTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    subsubcategory = models.ForeignKey(SubSubCategoryTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    is_veg = models.BooleanField(default=True) 
    # image = models.FileField(upload_to='item_images/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    # variant = models.ForeignKey(ItemVariantTable, on_delete=models.CASCADE, null=True, blank=True)
    # voice_description = models.FileField(upload_to='voice_descriptions/', null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    preparation_time = models.FloatField(default=0.0)
    branches = models.ManyToManyField('BranchTable', related_name='item_branch', blank=True)
    inventory = models.IntegerField(default=0)
    calories = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fast_delivery = models.BooleanField(default=False)
    newest = models.BooleanField(default=True)
    available = models.BooleanField(default=True, null=True, blank=True)

    def __str__(self):
        return self.name
    
class ItemImageTable(models.Model):
    item = models.ForeignKey(ItemTable, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='item_images/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.item.name}"

    
class ItemVariantTable(models.Model):
    item = models.ForeignKey(ItemTable, on_delete=models.CASCADE, related_name='variants', null=True, blank=True)
    variant_name = models.CharField(max_length=50)
    price = models.FloatField()

    def __str__(self):
        return f"{self.item.name} - {self.variant_name} - ₹{self.price}"    

class VoiceDescriptionTable(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ml', 'Malayalam'),
        ('hi', 'Hindi'),
        ('ar', 'Arabic'),
        # Add more if needed
    ]
    item = models.ForeignKey('ItemTable', on_delete=models.CASCADE, related_name='voice_descriptions')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    audio_file = models.FileField(upload_to='voice_descriptions/')
    
    def __str__(self):
        return f"{self.item.name} - {self.get_language_display()}"


class AddonTable(models.Model):
    item = models.ForeignKey(ItemTable, on_delete=models.CASCADE, related_name='addons')
    name = models.CharField(max_length=100)
    quantity = models.IntegerField( default=1, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='addon_images/', null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Addon for {self.item.name})"
    


import pytz

from django.db import models
from django.utils.timezone import now

class OfferTable(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    startdate = models.DateTimeField(null=True, blank=True)
    enddate = models.DateTimeField(null=True, blank=True)
    branch = models.ForeignKey(BranchTable, on_delete=models.CASCADE, null=True, blank=True)
    offer_percentage = models.FloatField(null=True, blank=True)
    itemid = models.ForeignKey(ItemTable, on_delete=models.CASCADE, related_name='offers')
    offerdescription = models.CharField(max_length=100, null=True, blank=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        ist = pytz.timezone('Asia/Kolkata')
        current_time = now().astimezone(ist)

        print("Saving Offer:", self.name)
        print("Current Time (IST):", current_time)
        print("Start Time:", self.startdate)
        print("End Time:", self.enddate)

        if self.startdate and self.enddate:
            self.is_active = self.startdate <= current_time <= self.enddate
            print("Offer is_active:", self.is_active)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    

class RatingTable(models.Model):
    RATING_TYPE_CHOICES =  [
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
    price = models.FloatField(null=True, blank=True)
    addon = models.ManyToManyField(AddonTable, blank=True)   # ✅ addons linked here
    variant = models.ForeignKey(ItemVariantTable, on_delete=models.SET_NULL, null=True, blank=True)
    instruction = models.CharField(max_length=200, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.FloatField(null=True, blank=True) 

    def __str__(self):
        return f"{self.userid} - {self.fooditem} x {self.quantity}" 
    
class WishlistTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='wishlist_items')
    fooditem = models.ForeignKey(ItemTable, on_delete=models.CASCADE, related_name= 'wishlist_entries')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.userid} - {self.fooditem}"
    

class OrderItemTable(models.Model):
    order = models.ForeignKey(OrderTable, on_delete=models.CASCADE, related_name='order_item',null=True, blank=True)
    itemname = models.ForeignKey(ItemTable, on_delete=models.CASCADE, related_name='itemname')
    quantity = models.CharField(max_length=100, blank=True, null=True, default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    instruction = models.TextField(null=True, blank=True)
    variant = models.ForeignKey(ItemVariantTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='variant_items')
    addon = models.ForeignKey(ItemTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='addon_order_items')
    def __str__(self):
        return f"{self.order} - {self.itemname} x {self.quantity}"
    

class DeliveryTable(models.Model):
    order = models.ForeignKey(OrderTable, on_delete=models.CASCADE, related_name='order_items',null=True, blank=True)
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='deliveries_info')
    name = models.CharField(max_length=400)
    address = models.ForeignKey(AddressTable, on_delete=models.CASCADE, related_name='deliveries', null=True, blank=True)
    # latitude = models.FloatField(null=True, blank=True)
    # longitude = models.FloatField(null=True, blank=True)
    # voice_instruction = models.FileField(upload_to='delivery_instructions/', null=True, blank=True) 
    phone = models.CharField(max_length=15)
    instruction = models.CharField(max_length=450, null=True, blank=True)
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


class PrinterTable(models.Model):
    name = models.CharField(max_length=100, unique=True)
    branch = models.ForeignKey(BranchTable, on_delete=models.CASCADE, related_name='printers')
    subcategories = models.ForeignKey(SubCategoryTable, on_delete=models.CASCADE, related_name='printers')
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return self.name

class ManagerTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='manager_profile')
    BranchID = models.ForeignKey(BranchTable, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=100, null=True, blank=True)
    image = models.FileField(upload_to='manager_images/', null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    idproof = models.FileField(upload_to='manager_idproofs/', null=True, blank=True)
    qualification = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"

class WaiterTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='waiter_profile')
    BranchID = models.ForeignKey(BranchTable, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.CharField(max_length=100, null=True, blank=True)
    image = models.FileField(upload_to='waiter_images/', null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    idproof = models.FileField(upload_to='waiter_idproofs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"


class FloorTable(models.Model):
    branch = models.ForeignKey(BranchTable, on_delete=models.CASCADE, related_name='no_of_floors')
    floor_number = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)  # Optional: e.g., "Ground Floor", "First Floor"
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('branch', 'floor_number')
        ordering = ['branch', 'floor_number']

    def __str__(self):
        return f"{self.branch.name} - Floor {self.floor_number}{f' ({self.name})' if self.name else ''}"

class DiningTable(models.Model):
    branch = models.ForeignKey(BranchTable, on_delete=models.CASCADE, related_name='dining_tables')
    floor = models.IntegerField(null=True, blank=True)
    table_number = models.CharField(max_length=20)  # e.g. "T1", "A2", etc.
    seating_capacity = models.IntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('branch', 'floor', 'table_number')  # prevent duplicate tables

    def __str__(self):
        return f"Table {self.table_number} - Floor {self.floor} @ {self.branch.name}"

    
class BillTable(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('ONLINE', 'Online Payment'),
    ]

    PAYMENT_CHANNEL_CHOICES = [
        ('BY_HAND', 'By Hand'),
        ('ONLINE', 'Online'),
    ]

    order = models.OneToOneField('OrderTable', on_delete=models.CASCADE, related_name='bill')
    branch = models.ForeignKey('BranchTable', on_delete=models.SET_NULL, null=True, related_name='bills')
    table = models.ForeignKey('DiningTable', on_delete=models.SET_NULL, null=True, blank=True, related_name='bills')
    waiter = models.ForeignKey('LoginTable', on_delete=models.SET_NULL, null=True, related_name='bills_generated')
    
    bill_number = models.CharField(max_length=50, unique=True)
    subtotal = models.FloatField(default=0.0)
    tax = models.FloatField(default=0.0)
    discount = models.FloatField(default=0.0)
    total_amount = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, default='PENDING')

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True
    )
    payment_channel = models.CharField(
        max_length=20,
        choices=PAYMENT_CHANNEL_CHOICES,
        null=True,
        blank=True
    )
    paid_at = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Bill #{self.bill_number} for Order #{self.order.id}"

    # def calculate_total(self):
    #     self.total_amount = self.subtotal + self.tax - self.discount
    #     self.save()

class CarouselTable(models.Model):
    image = models.FileField(upload_to='carousel_images/')
    offer = models.ForeignKey(OfferTable, on_delete=models.CASCADE, null=True, blank=True, related_name='carousel_offers')
    branch = models.ManyToManyField(BranchTable)
    offer_percentage = models.FloatField(default=0.0, null=True, blank=True)
    startdate = models.DateTimeField(null=True, blank=True)
    enddate = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.offer} - {self.branch} ({self.offer_percentage}%)"

class SpotlightTable(models.Model):
    image = models.FileField(upload_to='spotlight_images/')
    category = models.ForeignKey(SubCategoryTable, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(BranchTable, on_delete=models.CASCADE, blank=True, null=True)
    offer_percentage = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.branch} ({self.offer_percentage}%)"
    


class ChatMessage(models.Model):
    order = models.ForeignKey(OrderTable, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(ProfileTable, on_delete=models.CASCADE, null=True, blank=True)
    delivery_boy = models.ForeignKey(DeliveryBoyTable, on_delete=models.CASCADE, null=True, blank=True)
    sender_type = models.CharField(max_length=20, choices=[('USER', 'User'), ('DELIVERYBOY', 'DeliveryBoy')])
    
    message_type = models.CharField(
        max_length=10,
        choices=[('TEXT', 'Text'), ('IMAGE', 'Image'), ('AUDIO', 'Audio')],
        default='TEXT'
    )
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='chat/images/', blank=True, null=True)
    audio = models.FileField(upload_to='chat/audio/', blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender_type} -> {self.message_type}'
    
class UserFeedbackTable(models.Model):
    order = models.ForeignKey(OrderTable, on_delete=models.CASCADE)
    delivery_boy = models.ForeignKey(DeliveryBoyTable, on_delete=models.CASCADE)
    rating = models.FloatField()
    feedback = models.TextField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for Order #{self.order.id} by Delivery Boy {self.delivery_boy.id}"
    

class CreditUser(models.Model):
    Name = models.CharField(max_length=100, null=True, blank=True)
    Email = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


class OfflineOrders(models.Model):
    ORDER_TYPES = [
        ('DINE_IN', 'Dine In'),
        ('TAKEAWAY', 'Takeaway'),
        ('ONLINEDELIVERY', 'Online Delivery'),
    ]

    order_type = models.CharField(max_length=20, choices=ORDER_TYPES, default='DINE_IN')

    # Dining-related fields
    table = models.ForeignKey("DiningTable", on_delete=models.CASCADE, null=True, blank=True)
    waiter = models.ForeignKey("WaiterTable", on_delete=models.CASCADE, null=True, blank=True)

    # Delivery-related fields
    deliveryboy = models.ForeignKey("DeliveryBoyTable", on_delete=models.CASCADE, null=True, blank=True)
    credit_user = models.ForeignKey("CreditUser", on_delete=models.CASCADE, null=True, blank=True)

    # Customer details (for takeaway & online)
    customer_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    # Payment & totals
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment = models.CharField(max_length=100, null=True, blank=True)

    # Meta info
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"Order #{self.id} - {self.order_type}"


class OfflineOrderItems(models.Model):
    order = models.ForeignKey(OfflineOrders, on_delete=models.CASCADE, related_name="order_items")
    item = models.ForeignKey("ItemTable", on_delete=models.CASCADE)
    variant = models.ForeignKey("ItemVariantTable", on_delete=models.SET_NULL, null=True, blank=True)

    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        variant_display = self.variant.variant_name if self.variant else "No Variant" 
        return f"Order {self.order.id} - {self.item.name} ({variant_display}) x {self.quantity}"

