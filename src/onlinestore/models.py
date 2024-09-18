from django.db import models
from decimal import Decimal
from django.contrib.auth import get_user_model

User = get_user_model()


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='user_address')
    session_key = models.CharField(max_length=120, blank=True, null=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=20, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    region_group = models.CharField(max_length=255, null=True, blank=True)
    province = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    barangay = models.CharField(max_length=255, null=True, blank=True)
    line1 = models.CharField(max_length=255, null=True, blank=True)
    line2 = models.CharField(max_length=255, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    message = models.TextField(blank=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)


class SiteSetting(models.Model):
    key = models.CharField(max_length=255, unique=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.key}: {self.value}"

    @classmethod
    def get_fixed_shipping_fee(cls):
        try:
            fee = cls.objects.get(key='fixed_shipping_fee').value
            return Decimal('0.00') if fee == Decimal('0.00') else fee
        except cls.DoesNotExist:
            return Decimal('0.00')

    @classmethod
    def get_max_order_quantity(cls):
        try:
            max_qty = cls.objects.get(key='max_order_quantity').value
            return Decimal('0.00') if max_qty == Decimal('0.00') else max_qty
        except cls.DoesNotExist:
            return Decimal('0.00')
