from django.db import models
from django.urls import reverse
from django.utils import timezone
from addresses.models import Address
from billing.models import Customer
from ecommerce.utils import unique_order_id_generator
from django.db.models.signals import pre_save
from products.models import Product


ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded'),
)


class Order(models.Model):
    customer            = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order_id            = models.CharField(max_length=120, blank=True, unique=True)
    session_key         = models.CharField(max_length=120, blank=True, null=True, unique=True)
    shipping_address    = models.ForeignKey(Address, null =True, blank=True, on_delete=models.CASCADE, related_name='shipping_address')
    contact_number      = models.CharField(max_length=15, blank=True, null=True)
    complete            = models.BooleanField(default=False, null=True, blank=False)
    active              = models.BooleanField(default=True)
    created_at          = models.DateTimeField(default=timezone.now)
    ordered_items       = models.ManyToManyField(Product, blank=True)
    
    
    def __str__(self):
        return str(self.order_id)
    
    def get_absolute_url(self):
        return reverse("orders:detail", kwargs={'order_id': self.order_id})
    
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
        total = self.product.customer_price * self.quantity
        return total