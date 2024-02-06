from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.urls import reverse
from django.apps import apps
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db import transaction

User = get_user_model()

    
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='customer')
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    referrer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='referred_customers')
    
    is_guest = models.BooleanField(default=False)
    
    def __str__(self):
        return self.email

    def get_cart_items_count(self):
        Order = apps.get_model('orders', 'Order')
        orders = Order.objects.filter(customer=self)
        return sum(order.orderitem_set.count() for order in orders)

    
    @classmethod
    def get_or_create_customer(cls, user, request, referrer_id=None):
        User = get_user_model()
        if user.is_authenticated:
            referrer = User.objects.filter(id=referrer_id).first() if referrer_id else None
            if referrer is None:
                # If referrer_id is not provided or no User with that id exists, use the admin's User object as the referrer
                referrer = User.objects.filter(is_superuser=True).first()
            user_instance = User.objects.filter(id=user.id).first()
            if user_instance is None:
                return None, False
            customer, created = cls.objects.get_or_create(user=user_instance, referrer=referrer, defaults={'email': user_instance.email})
        else:
            # Handle anonymous users here
            from user.utils import create_or_get_guest_user
            customer = create_or_get_guest_user(request)
            created = False
        return customer, created


    