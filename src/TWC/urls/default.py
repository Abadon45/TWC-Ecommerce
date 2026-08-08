from django.urls import path, include, re_path
from django.conf.urls import handler404
from django.conf.urls.static import static
from onlinestore.views import *
from ..views import EmailFormView

urlpatterns = [
    path('mail-success/', TemplateView.as_view(template_name='mail-success.html'), name="mail_success"),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name="terms"),
    path(
        'return-policy/',
        TemplateView.as_view(
            template_name='return-policy.html',
            extra_context={'title': 'TWC Store | Return Policy'}
        ),
        name="return_policy"
    ),
    path(
        'terms-of-service/',
        TemplateView.as_view(
            template_name='terms-of-service.html',
            extra_context={'title': 'TWC Store | Terms of Service'}
        ),
        name="terms_of_service"
    ),
    path('test-email/', EmailFormView.as_view(), name="test_email"),
    path('shop/', include('TWC.urls.shop', namespace='shop')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('', IndexView.as_view(), name="home_view"),

]

handler404 = Handle404View.as_view()


