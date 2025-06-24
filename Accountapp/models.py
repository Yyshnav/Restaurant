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
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
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

class ItemTable(models.Model):
    TYPE_CHOICES = [
        ('VEG', 'Vegetarian'),
        ('NONVEG', 'Non-Vegetarian'),
        ('BEVERAGE', 'Beverage'),
        ('DESSERT', 'Dessert'),
    ]
    name = models.CharField(max_length=100)
    category = models.ForeignKey(CategoryTable, on_delete=models.CASCADE, related_name='items')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    image = models.ImageField(upload_to='item_images/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fast_delivery = models.BooleanField(default=False)
    newest = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name
            
class OfferTable(models.Model):
    name = models.CharField(max_length=100)
    startdate = models.DateField()
    enddate = models.DateField()
    offer_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    itemid = models.ForeignKey(ItemTable, on_delete=models.CASCADE, related_name='offers')
    offerdescription = models.TextField(null=True, blank=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class RatingTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='ratings')
    itemid = models.ForeignKey(ItemTable, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField()
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.userid} rated {self.itemid} - {self.rating}"
    
class CartTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='cart_items')
    fooditem = models.ForeignKey(ItemTable, on_delete=models.CASCADE, related_name='cart_entries')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

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
    totalamount = models.DecimalField(max_digits=10, decimal_places=2)
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
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    instruction = models.TextField(null=True, blank=True)
    addon = models.ForeignKey(ItemTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='addon_order_items')

    def __str__(self):
        return f"{self.order} - {self.itemname} x {self.quantity}"
    
class DeliveryTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='deliveries_info')
    name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    phone = models.CharField(max_length=15)
    instruction = models.TextField(null=True, blank=True)  # Can store text or a reference to a voice file
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"
    
class ComplaintTable(models.Model):
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='complaints')
    deliveryid = models.ForeignKey(DeliveryTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    complaint = models.TextField()
    image = models.ImageField(upload_to='complaint_images/', null=True, blank=True)
    reply = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Complaint by {self.userid} (Delivery: {self.deliveryid})"
    
class DeliveryBoyTable(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    image = models.ImageField(upload_to='deliveryboy_images/', null=True, blank=True)
    idproof = models.ImageField(upload_to='deliveryboy_idproofs/', null=True, blank=True)
    userid = models.ForeignKey(LoginTable, on_delete=models.CASCADE, related_name='deliveryboy_profile')

    def __str__(self):
        return f"{self.name} ({self.phone})"
    
