from django.db import models
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

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


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_slug = models.CharField(max_length=255)
    score = models.IntegerField(default=3)

    class Meta:
        unique_together = ('user', 'product_slug')


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    product_slug = models.CharField(max_length=255)
    rating = models.OneToOneField(Rating, on_delete=models.CASCADE, related_name='review')
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user} on {self.product_slug}'


@receiver(post_save, sender=Rating)
def create_review_for_rating(sender, instance, created, **kwargs):
    if created:
        Review.objects.create(user=instance.user, product_slug=instance.product_slug, rating=instance)


@receiver(post_save, sender=Rating)
def update_product_aggregate_rating(sender, instance, **kwargs):
    instance.product.update_aggregate_rating()
