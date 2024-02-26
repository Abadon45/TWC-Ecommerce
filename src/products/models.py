from django.db import models
from django.utils.text import slugify
from TWC.utils import upload_image_path_admin
from django.urls import reverse
                            
    
class Product(models.Model):
    PRODUCT_CATEGORY_1_CHOICES = [
        ('promos', 'Promos'),
        ('sante', 'Sante Product'),
        ('twc', 'TWC Product'),
        ('chingu', 'Chingu'),
        ('mood', 'Mood Timepieces'),
        ('sante-package', 'Sante | Package'),
    ]

    PRODUCT_CATEGORY_2_CHOICES = [
        ('sante-nutraceutical', 'Sante | Nutraceutical'),
        ('sante-beverage', 'Sante | Beverage'),
        ('sante-intimate_care', 'Sante | Intimate Care'),
        ('twc-freebie', 'TWC | Freebie'),
        ('chingu-bundle', 'Chingu | Bundle'),
        ('mood-bundle', 'Mood Timepieces | Bundle'),
        ('promo', 'Promos'),
    ]
    
    sku = models.CharField('SKU', max_length=255, null=True, blank=True)
    slug = models.CharField('slug', max_length=255, null=True, blank=True)
    category_1 = models.CharField('Category 1', max_length=20, default='sante', choices=PRODUCT_CATEGORY_1_CHOICES)
    category_2 = models.CharField('Category 2', max_length=20, default='nutraceutical', choices=PRODUCT_CATEGORY_2_CHOICES)

    name = models.CharField('Product Name', max_length=255, null=True, blank=True)
    description_1 = models.TextField('Short Description', blank=True, null=True)
    description_2 = models.TextField('Long Description', blank=True, null=True)
    feature = models.TextField('Features', blank=True, null=True)
    advantage = models.TextField('Advantages', blank=True, null=True)
    benefit = models.TextField('Benefits', blank=True, null=True)
    specification = models.TextField('Specifications', blank=True, null=True)
    image_1 = models.ImageField('Image 1', upload_to=upload_image_path_admin, blank=True, null=True)
    image_2 = models.ImageField('Image 2', upload_to=upload_image_path_admin, blank=True, null=True)
    image_3 = models.ImageField('Image 3', upload_to=upload_image_path_admin, blank=True, null=True)
    image_4 = models.ImageField('Image 4', upload_to=upload_image_path_admin, blank=True, null=True)
    image_5 = models.ImageField('Image 5', upload_to=upload_image_path_admin, blank=True, null=True)

    supplier_price  = models.DecimalField('Supplier Price', default=0.00, max_digits=20, decimal_places=2)
    franchisee_price = models.DecimalField('Franchisee Price', default=0.00, max_digits=20, decimal_places=2)
    distributor_price = models.DecimalField('Member Price', default=0.00, max_digits=20, decimal_places=2)
    seller_price = models.DecimalField('Seller Price', default=0.00, max_digits=20, decimal_places=2)
    customer_price = models.DecimalField('Customer Price', default=0.00, max_digits=20, decimal_places=2)

    franchisee_fee = models.DecimalField('Branch Markup | Franchisee Fee', default=0.00, max_digits=20, decimal_places=2)
    fulfiller_fee = models.DecimalField('Fulfiller Fee', default=0.00, max_digits=20, decimal_places=2)
    transaction_fee = models.DecimalField('Transaction Fee', default=0.00, max_digits=20, decimal_places=2)

    shipping_qty = models.IntegerField('Shipping Quantity', default=1)
    barley_point = models.IntegerField('Barley Point', default=0)

    is_for_autoship  = models.BooleanField(default=False)
    is_for_vw        = models.BooleanField(default=False)
    is_digital       = models.BooleanField(default=False)

    active = models.BooleanField('Active', default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sku
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)
        
    def get_category_1_display(self):
        return dict(self.PRODUCT_CATEGORY_1_CHOICES).get(self.category_1, '')

    def get_category_2_display(self):
        return dict(self.PRODUCT_CATEGORY_2_CHOICES).get(self.category_2, '')

    class Meta:
        ordering = ['-timestamp']

    def is_in_cart(self, user):
        cart = self.cart_set.filter(product=self, user=user)
        if cart.exists():
            return True
        else:
            return False
    
    # def get_absolute_url(self):
    #     # Replace 'product_detail' with the name of your view for displaying a single product
    #     return reverse('product_detail', args=[str(self.id)])

