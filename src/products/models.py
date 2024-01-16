from django.db import models
from django.utils.text import slugify
                            

class Category(models.Model):
    FASHION_ACCESSORIES = 'Fashion & Accessories'
    ELECTRONICS = 'Electronics'
    HEALTH = 'Health'

    CATEGORY_CHOICES = [
        (FASHION_ACCESSORIES, 'Fashion & Accessories'),
        (ELECTRONICS, 'Electronics'),
        (HEALTH, 'Health'),
    ]

    name = models.CharField(max_length=255, choices=CATEGORY_CHOICES, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    CATEGORY_CHOICES = [
        (1, 'Fashion & Accessories'),
        (2, 'Electronics'),
        (3, 'Health'),
    ]
    BRAND_CHOICES = [
        (1, 'Apple'),
        (2, 'Samsung'),
        (3, 'Sante'),
    ]
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    category = models.IntegerField(choices=CATEGORY_CHOICES, blank=True, null=True)
    brand = models.IntegerField(choices=BRAND_CHOICES, blank=True, null=True)
    sku = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField(blank=True, null=True)
    stock_unit = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
 
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1

            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = unique_slug

        super().save(*args, **kwargs)
    def __str__(self):
        
        return str(self.name)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'category': str(self.category),
            'brand': self.brand,
            'sku': self.sku,
            'price': str(self.price),
            'discount_price': str(self.discount_price) if self.discount_price is not None else None,
            'stock': self.stock,
            'stock_unit': self.stock_unit,
            'description': self.description,
        }

    
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='img/')
    

