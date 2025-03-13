from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import os
from logging.handlers import RotatingFileHandler

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development setting - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-)!a@6)s)$_u_o6*b7&#vqo++i)i5f^$_8nid!r0w^wm3#w47$y'
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN",
                               "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2Mjk0MzM5OSwiaWF0IjoxNzMxNDA3Mzk5LCJqdGkiOiJiNjNjMTNlYzdkNjA0OGYxYmE3NDU2NzQwNmFiZTU1ZSIsInVzZXJfaWQiOjE5ODgzfQ.CoHhMbk89oiwTVKk-Y7VAaMBa3WkzwrLRJo-6IKTZ70")

XENDIT_API_KEY = os.environ.get("XENDIT_API_KEY",
                                '_gyFfI1cqWWOTpXRWcfg1RMPC3UkCTAfAVsqSDl6fjFuZqs6mFaPZw9yzqO7B5')

HOST_DOMAIN = os.environ.get("HOST_DOMAIN", "twcako")

# TWCAKO API
SHOP_PRODUCTS_API = f'https://dashboard.{HOST_DOMAIN}.com/shop/api/get-product/?'
SHOP_PRODUCT_DETAIL_API = f'https://dashboard.{HOST_DOMAIN}.com/shop/api/get-product/?slug={{product_slug}}'
PRODUCT_URL_API = f'https://dashboard.{HOST_DOMAIN}.com/shop/api/get-product/?slug='
REFRESH_TOKEN_API = f'https://dashboard.{HOST_DOMAIN}.com/order/api/get-access-token/'
ORDER_URL_API = f'https://dashboard.{HOST_DOMAIN}.com/order/api/create-order/'
VW_INVENTORY_API = f"https://dashboard.{HOST_DOMAIN}.com/account/api/check-username/{{username}}/vwinventory/"
PH_NUMBERS_PREFIXES_API = f"https://dashboard.{HOST_DOMAIN}.com/addresses/api/ph-number-prefixes/"
AUTH_API_URL = f"https://dashboard.{HOST_DOMAIN}.com/api/auth/"
REGISTER_USER_API_URL = f"https://dashboard.{HOST_DOMAIN}.com/account/api/register/"
CHECK_USERNAME_API_URL = f"https://dashboard.{HOST_DOMAIN}.com/account/api/check-username/{{username}}/"
FETCH_ORDERS_API_URL = f"https://dashboard.{HOST_DOMAIN}.com/order/api/fetch-order/{{username}}"
UPDATE_PROFILE_API_URL = f"https://dashboard.{HOST_DOMAIN}.com/account/api/update-profile/{{username}}"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*', ]

USE_X_FORWARDED_HOST = True

SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'django_celery_results',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'user',
    'TWC',
    'onlinestore',
    'cart',
    'django_hosts',
    'django.contrib.sites',
    'rest_framework',
    'rest_framework.authtoken',
]

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}

MIDDLEWARE = [
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # API Authentication
    'user.middleware.APISessionAuthenticationMiddleware',

    # custom middlewares
    'TWC.middleware.SubdomainMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
    'TWC.middleware.RedirectToWWW',
    'TWC.middleware.DynamicCSRFMiddleware',
    'TWC.middleware.CurrentDomainMiddleware',
    'TWC.middleware.SubdomainSessionMiddleware',

]

AUTH_USER_MODEL = 'user.User'

ROOT_URLCONF = 'TWC.urls'
ROOT_HOSTCONF = 'TWC.hosts'
DEFAULT_HOST = 'wildcard'
CSRF_TRUSTED_ORIGINS = ['https://twconline.store', 'https://twcstoredevtest.com']
CORS_ALLOWED_ORIGINS = [
    "https://www.twconline.store",
    "http://localhost:8000",
    "https://www.twcstoredevtest.com",
    "https://dashboard.twcstoredevtest.com",
    "https://dashboard.twconline.store"

]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'onlinestore', 'templates'),
            os.path.join(BASE_DIR, 'templates', 'allauth'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'onlinestore.context_processors.referrer',
                'onlinestore.context_processors.cart_items',
                'onlinestore.context_processors.facebook_pixel_id',
                'onlinestore.context_processors.ph_number_prefixes',
                'TWC.context_processors.main_site_url',
                'TWC.context_processors.site_urls',
            ],
        },
    },
]

ACCOUNT_CONTEXT_PROCESSORS = [
    'django.template.context_processors.request',
]

WSGI_APPLICATION = 'TWC.wsgi.application'

# Database
POSTGRES_DB = os.environ.get("POSTGRES_DB", 'twcmart')
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", 'VjIT0hyTEzHSwV-yEpGh-l7uNoieqZ-YhapAj4Qf2r4')
POSTGRES_USER = os.environ.get("POSTGRES_USER", 'twcdev')
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", '172.104.160.121')
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': POSTGRES_HOST,
        'PORT': POSTGRES_PORT,
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Manila'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR / "static"),)
STATIC_ROOT = os.path.join(BASE_DIR, "static_root")

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR / 'media')

# CElERY SETTINGS
CELERY_BROKER_URL = 'redis://172.234.49.190:6379'
CELERY_RESULT_BACKEND = 'redis://172.234.49.190:6379'

broker_connection_retry_on_startup = True

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TIMEZONE = TIME_ZONE

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# SENDGRID EMAIL

SENDGRID_API_KEY = ''
username = 'ZXZnZXJvbmlsbGE='
password = 'dmVuZGljczIwMTU='

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_MAIN = 'TWCAKO <support@twcako.com>'
EMAIL_HOST_PASSWORD = ''
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True

EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False

DEFAULT_FROM_EMAIL = EMAIL_MAIN
SERVER_EMAIL = EMAIL_MAIN

ACCOUNT_EMAIL_TEMPLATE_PASSWORD_RESET = 'login/password_reset_email.html'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'TWC', 'logs', 'error.log'),
            'maxBytes': 1024 * 1024,  # 1 MB
            'backupCount': 5,
        },
    },
    'root': {
        'handlers': ['error_file'],
        'level': 'ERROR',
    },
}

# Application definition
AUTHENTICATION_BACKENDS = ["user.auth_backends.APIAuthenticationBackend"]
