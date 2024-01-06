from django.db import models
from billing.models import Customer


class Address(models.Model):
    address_type = models.CharField(max_length=120)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255)
    postcode = models.CharField(max_length=20)
    message = models.TextField(blank=True)
    
    def __str__(self):
        return str(self.customer)
    