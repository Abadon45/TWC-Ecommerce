from django.db import models
from django.contrib.auth import get_user_model
from billing.models import Customer

User = get_user_model()


class Address(models.Model):
    customer        = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    user            = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    session_key     = models.CharField(max_length=120, blank=True, null=True)
    first_name      = models.CharField(max_length=255, null=True, blank=True)
    last_name       = models.CharField(max_length=255, null=True, blank=True)
    email           = models.EmailField(max_length=20, null=True, blank=True)
    phone           = models.CharField(max_length=20, null=True, blank=True)
    region          = models.CharField(max_length=255, null=True, blank=True)
    province        = models.CharField(max_length=255, null=True, blank=True)
    city            = models.CharField(max_length=255, null=True, blank=True)
    barangay        = models.CharField(max_length=255, null=True, blank=True)
    line1           = models.CharField(max_length=255, null=True, blank=True)
    line2           = models.CharField(max_length=255, null=True, blank=True)
    postcode        = models.CharField(max_length=20, null=True, blank=True)
    message         = models.TextField(blank=True, null=True)
    is_default      = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.user)
    