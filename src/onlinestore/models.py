from django.db import models
from decimal import Decimal


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
