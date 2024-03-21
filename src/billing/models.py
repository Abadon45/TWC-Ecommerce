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

from user.utils import create_or_get_guest_user

User = get_user_model()

    
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='customer')
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    referrer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='referred_customers')
    
    is_guest = models.BooleanField(default=False)
    
    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return self.email

    def get_cart_items_count(self):
        Order = apps.get_model('orders', 'Order')
        orders = Order.objects.filter(customer=self)
        return sum(order.orderitem_set.count() for order in orders)

    
    @classmethod
    def get_or_create_customer(cls, user, request, referrer_code=None):
        referrer = None
        if referrer_code:
            try:
                referrer = User.objects.get(id=referrer_code)
            except User.DoesNotExist:
                print(f"No user found with referrer_code: {referrer_code}")
                referrer = None
            else:
                print(f"User found with referrer_code: {referrer_code}")

        if user.is_authenticated:
            print(f"User is authenticated: {user.username}")
            customer, created = cls.objects.get_or_create(user=user, defaults={'email': user.email})
        else:
            print(f"User is not authenticated")
            customer = create_or_get_guest_user(request, referrer_id=referrer.id if referrer else None)
            created = False  # Since create_or_get_guest_user always returns an existing customer, created is False

        print(f"Customer: {customer}, Created: {created}")
        return customer, created
    