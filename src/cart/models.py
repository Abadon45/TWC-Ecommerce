from django.db import models
from django.contrib.auth import get_user_model
from onlinestore.models import SiteSetting


import logging

User = get_user_model()

logger = logging.getLogger(__name__)


COURIER_CHOICES = (
    ('j&t', 'J&T'),
    ('lbc', 'LBC'),
    ('gogoxpress', 'GogoXpress'),
)

POUCH_CHOICES = (
    ('sakto pack', 'Sakto Pack'),
    ('small', 'Small'),
    ('medium', 'Medium'),
    ('large', 'Large'),
    ('box', 'Box'),
    ('others', 'Others'),
)

FULFILLER_CHOICES = (
    ('other', 'Other'),
    ('mandaluyong', 'Mandaluyong HUB'),
    ('sante valenzuela', 'Sante Valenzuela'),
    ('sante cdo', 'Sante CDO'),
)


class Courier(models.Model):
    tracking_number = models.CharField(max_length=120, blank=True, null=True, unique=True)
    courier = models.CharField(max_length=20, choices=COURIER_CHOICES, null=True, blank=True)
    pouch_size = models.CharField(max_length=20, choices=POUCH_CHOICES, null=True, blank=True)
    actual_shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    pickup_date = models.DateField(verbose_name='Pickup Date', null=True, blank=True)
    fulfiller = models.CharField(max_length=20, choices=FULFILLER_CHOICES, default='other')
    paid_by_fulfiller = models.BooleanField(default=True)
    booking_notes = models.TextField(blank=True)

    def __str__(self):
        return self.fulfiller


# class Voucher(models.Model):
#     DISCOUNT_TYPE_CHOICES = [
#         ('fixed', 'Fixed Amount'),
#         ('percent', 'Percentage'),
#         ('free_shipping', 'Free Shipping'),
#         ('shipping_discount', 'Shipping Discount'),
#     ]
#
#     code = models.CharField(max_length=50, unique=True)
#     discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
#     discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     min_order_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     valid_from = models.DateTimeField()
#     valid_to = models.DateTimeField()
#     active = models.BooleanField(default=True)
#     usage_limit = models.IntegerField(null=True, blank=True)
#     users_used = models.ManyToManyField(User, through='VoucherUsage')
#
#     def is_valid(self):
#         """ Check if the voucher is valid (active, not expired) """
#         if not self.active:
#             return False
#         return True
#
#     def get_discount_value(self):
#         return self.discount_value
#
#     def get_reduced_shipping_value(self):
#         return self.reduced_shipping_value
#
#     def __str__(self):
#         return self.code


# ORDER_STATUS_CHOICES = (
#     ('pending', 'Pending'),
#     ('for-booking', 'For Booking'),
#     ('for-pickup', 'For Pickup'),
#     ('shipping', 'Shipping'),
#     ('delivered', 'Delivered'),
#     ('paid', 'Paid'),
#     ('bp-encoded', 'BP Encoded'),
#     ('vw-paid', 'VW Paid'),
#     ('rts', 'RTS'),
#     ('returned', 'Returned'),
# )


# class VoucherUsage(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE)
#     used_on = models.DateTimeField(auto_now_add=True)
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#
#     class Meta:
#         unique_together = ('user', 'voucher')
