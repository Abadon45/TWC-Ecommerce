from django.conf import settings
from django.core.validators import RegexValidator, validate_email
from django.apps import apps
from django.urls import reverse
from django.contrib.sites.models import Site
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from TWC.utils import upload_image_path


alphanumeric = RegexValidator(regex=r'^[0-9a-zA-Z]*$', message='The username must only contain letters and numbers.')


class UserManager(BaseUserManager):

    def create_user(self, username=None, password=None, is_active=True, is_staff=False,
                    is_admin=False):
        if not username:
            raise ValueError("Users must have a username")
        if not password:
            raise ValueError("Users must have a password")

        user_obj = self.model(username=username)
        user_obj.set_password(password)  # change user password
        user_obj.is_staff = is_staff
        user_obj.is_admin = is_admin
        user_obj.is_active = is_active
        user_obj.full_clean()  # validate the model
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, username, password=None):
        user = self.create_user(
            username,
            password=password,
            is_staff=True,
        )
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(
            username=username,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user
    
    def normalize_email(self, email):
        """
        Normalize the email by lowercasing the domain part of it
        """
        email_name, domain_part = email.strip().split('@')
        return '@'.join([email_name, domain_part.lower()])

class User(AbstractBaseUser):
    username        = models.CharField(verbose_name='Username', max_length=150, validators=[alphanumeric], unique=True, error_messages={'unique': _("A user with that username already exists."),})
    id_number       = models.CharField(verbose_name='ID Number', max_length=100, blank=True, null=True)
    mobile          = models.CharField(verbose_name='Mobile Number', max_length=100, blank=True, null=True, unique=True, db_index=True)
    email           = models.EmailField(verbose_name='Email Address', max_length=100, validators=[validate_email, ], blank=True, null=True,)
    messenger_link  = models.CharField(verbose_name='Messenger Link', max_length=255, blank=True, null=True)

    first_name      = models.CharField(verbose_name='First Name', max_length=100, blank=True, null=True)
    middle_name     = models.CharField(verbose_name='Middle Name', max_length=100, blank=True, null=True)
    last_name       = models.CharField(verbose_name='Last Name', max_length=100, blank=True, null=True)
    birth_date      = models.DateField(verbose_name='Date of Birth', blank=True, null=True)
    image           = models.ImageField(verbose_name='Profile Picture', upload_to=upload_image_path, null=True, blank=True)

    date_activated  = models.DateTimeField(verbose_name='Date Activated', blank=True, null=True)
    expiration_date = models.DateTimeField(verbose_name='Expiration Date', null=True, blank=True)

    is_seller       = models.BooleanField(default=False)
    is_member       = models.BooleanField(default=False)
    is_supplier     = models.BooleanField(default=False)

    is_expired      = models.BooleanField(default=True)
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    is_admin        = models.BooleanField(default=False)

    timestamp       = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return self.username if self.username else 'No username'
      
    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        if app_label == 'account':
            return self.is_admin
        else:
            return True
    
    def clean(self):
        if self.email is not None:
            User = get_user_model()
            self.email = User.objects.normalize_email(self.email)
        return super().clean()    

    def generate_affiliate_link(self):
        return f'http://www.{settings.SITE_DOMAIN}/shop/{self.username}{self.id}/'
        
    def get_referred_customers(self):
        try:
            Customer = apps.get_model('billing', 'Customer')
            return Customer.objects.filter(referrer=self)
        except ImproperlyConfigured:
            print("Error: Could not get the 'Customer' model from the 'billing' app.")
            return None

    def get_referred_orders(self):
        try:
            Order = apps.get_model('orders', 'Order')
            return Order.objects.filter(customer__in=self.get_referred_customers())
        except ImproperlyConfigured:
            print("Error: Could not get the 'Order' model from the 'orders' app.")
            return None

    def get_referred_customers_with_orders(self):
        return self.get_referred_customers().filter(order__isnull=False)

    def get_referred_customers_with_completed_orders(self):
        return self.get_referred_customers().filter(order__complete=True)
    
    
