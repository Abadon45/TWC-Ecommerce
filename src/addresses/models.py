from django.db import models
from billing.models import Customer


class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    province = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    barangay = models.CharField(max_length=255, null=True, blank=True)
    line1 = models.CharField(max_length=255, null=True, blank=True)
    line2 = models.CharField(max_length=255, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    message = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.customer)
    