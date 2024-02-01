from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.urls import reverse
from django.contrib.auth.models import User
from django.apps import apps

User = settings.AUTH_USER_MODEL

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    is_guest = models.BooleanField(default=False)
    
    def __str__(self):
        return self.email

    def get_cart_items_count(self):
        Order = apps.get_model('orders', 'Order')
        orders = Order.objects.filter(customer=self)
        return sum(order.orderitem_set.count() for order in orders)
    
    
    @classmethod
    def get_or_create_customer(cls, user, email):
        customer, created = cls.objects.get_or_create(user=user, email=email)
        return customer, created
    