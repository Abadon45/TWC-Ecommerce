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
        if self.user:
            return self.user.username
        else:
            return self.email