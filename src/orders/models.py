from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from addresses.models import Address
from billing.models import Customer
from ecommerce.utils import unique_order_id_generator
from django.db.models.signals import pre_save
from products.models import Product

from decimal import Decimal

import logging

User = get_user_model()

logger = logging.getLogger(__name__)


COURIER_CHOICES = (
    ('j&t', 'J&T'),
    ('lbc', 'LBC'),
    ('gogoxpress', 'GogoXpress'),
)    

POUCH_CHOICES = (
    ('sakto pack', 'Sakto Pack'),
    ('small', 'Small'),
    ('medium', 'Medium'),
    ('large', 'Large'),
    ('box', 'Box'),
    ('others', 'Others'),
) 

FULFILLER_CHOICES = (
    ('other', 'Other'),
    ('mandaluyong', 'Mandaluyong HUB'),
    ('sante valenzuela', 'Sante Valenzuela'),
    ('sante cdo', 'Sante CDO'),
)


class Courier(models.Model):
    tracking_number         = models.CharField(max_length=120, blank=True, null=True, unique=True)
    courier                 = models.CharField(max_length=20, choices=COURIER_CHOICES, null=True, blank=True)
    pouch_size              = models.CharField(max_length=20, choices=POUCH_CHOICES, null=True, blank=True)
    actual_shipping_fee     = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    pickup_date             = models.DateField(verbose_name='Pickup Date', null=True, blank=True)
    fulfiller               = models.CharField(max_length=20, choices=FULFILLER_CHOICES, default='other')
    paid_by_fulfiller       = models.BooleanField(default=True)
    booking_notes           = models.TextField(blank=True)
    
    def __str__(self):
        return self.fulfiller


ORDER_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('for-booking', 'For Booking'),
    ('for-pickup', 'For Pickup'),
    ('shipping', 'Shipping'),
    ('delivered', 'Delivered'),
    ('paid', 'Paid'),
    ('bp-encoded', 'BP Encoded'),
    ('vw-paid', 'VW Paid'),
    ('rts', 'RTS'),
    ('returned', 'Returned'),
)

PAYMENT_CHOICES = (
    ('none', 'None'),
    ('cod', 'Cash On Delivery'),
)



class Order(models.Model):
    customer            = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    user                = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    order_id            = models.CharField(max_length=120, blank=True, unique=True)
    session_key         = models.CharField(max_length=120, blank=True, null=True)
    shipping_address    = models.ForeignKey(Address, null =True, blank=True, on_delete=models.CASCADE, related_name='shipping_address')
    courier             = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method      = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='none')
    contact_number      = models.CharField(max_length=15, blank=True, null=True)
    complete            = models.BooleanField(default=False, null=True, blank=False)
    delivered           = models.BooleanField(default=False, null=True, blank=False)
    active              = models.BooleanField(default=True)
    created_at          = models.DateTimeField(default=timezone.now)
    ordered_items       = models.ManyToManyField(Product, blank=True)
    status              = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    total_quantity      = models.IntegerField(default=0, null=True, blank=True)
    total_amount        = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    shipping_fee        = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    supplier            = models.CharField(max_length=100, blank=True, null=True)
    subtotal            = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    seller_total        = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    distributor_total   = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    discount            = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    cod_amount          = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    sponsor_profit      = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    seller_profit       = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    
    
    def __str__(self):
        try:
            return f"Order #{str(self.order_id) or '(no order ID available)'}"
        except Exception as e:
            logger.error(f"Error in Order.__str__ method: {type(e)}, {e}")
            return f"Order (Error generating string representation)" 
        
    def save(self, *args, **kwargs):
        if self.subtotal is not None and self.shipping_fee is not None:
            self.total_amount = Decimal(self.subtotal) + Decimal(self.shipping_fee)
        super().save(*args, **kwargs)

    
    def get_absolute_url(self):
        return reverse("orders:detail", kwargs={'order_id': self.order_id})
    
    def calculate_total_qty(self):
        total_quantity  = sum(item.quantity for item in self.orderitem_set.all())
        return total_quantity 
    
    def calculate_subtotal(self):
        subtotal = sum(item.get_total for item in self.orderitem_set.all())
        return subtotal
    
    def calculate_seller_total(self):
        seller_total = sum(item.get_seller_total for item in self.orderitem_set.all())
        return seller_total
    
    def calculate_distributor_total(self):
        distributor_total = sum(item.get_distributor_total for item in self.orderitem_set.all())
        return distributor_total
    

    @classmethod
    def get_or_create_customer(cls, user, email):
        if user is not None:
            customer, created = cls.objects.get_or_create(user=user, email=email)
            return customer, created
        else:
            # Handle the case for guests (non-authenticated users)
            customer, created = cls.objects.get_or_create(email=email)
            return customer, created
    
    @property
    def get_cart_total(self):
        total = sum([item.quantity for item in self.orderitem_set.all()])
        return total
    
    @property
    def get_cart_items(self):
        total = sum([item.get_total for item in self.orderitem_set.all()])
        return total
    
    @property
    def subtotal(self):
        return self.calculate_subtotal()
    
    @property
    def seller_total(self):
        return self.calculate_seller_total()
    
    @property
    def distributor_total(self):
        return self.calculate_distributor_total()
    
    @property
    def total_quantity(self):
        return self.calculate_total_qty()
    
def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)

pre_save.connect(pre_save_create_order_id, sender=Order)
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    @property
    def get_total(self):
        if self.product is None:
            return Decimal('0.00')
        total = self.product.customer_price * self.quantity
        return total
    
    @property
    def get_seller_total(self):
        if self.product is None:
            return Decimal('0.00')
        total = self.product.seller_price * self.quantity
        return total
    
    @property
    def get_distributor_total(self):
        if self.product is None:
            return Decimal('0.00')
        total = self.product.distributor_price * self.quantity
        return total
        
        
# PAYMENT_STATUS_CHOICES = (
#         ('pending', 'Pending'), 
#         ('completed', 'Completed'), 
#         ('failed', 'Failed')
#     )
        
# class Payment(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
#     method = models.CharField(max_length=50)  # gcash, maya, credit_card, etc.
#     transaction_id = models.CharField(max_length=100, blank=True, null=True)
#     status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='pending') 
#     created_at = models.DateTimeField(auto_now_add=True)
        
