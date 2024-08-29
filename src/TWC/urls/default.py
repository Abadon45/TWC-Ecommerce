from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.urls import urlpatterns as auth_urlpatterns
from onlinestore.views import *
from ..views import EmailFormView

urlpatterns = [
    path('about/', AboutUsView.as_view(), name="about"),
    path('become-seller/', BecomeSellerView.as_view(), name="become_seller"),
    path('coming-soon/', TemplateView.as_view(template_name='coming-soon.html'), name="coming_soon"),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name="contact"),
    path('faqs/', TemplateView.as_view(template_name='faq.html'), name="faqs"),
    path('mail-success/', TemplateView.as_view(template_name='mail-success.html'), name="mail_success"),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name="privacy"),
    path('return/', TemplateView.as_view(template_name='return.html'), name="return"),
    path('team/', TemplateView.as_view(template_name='team.html'), name="team"),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name="terms"),
    path('test/', TemplateView.as_view(template_name='test.html'), name="test"),
    path('testimonial/', TemplateView.as_view(template_name='testimonial.html'), name="testimonial"),
    path('test-email/', EmailFormView.as_view(), name="test_email"),
    path('login/', include('TWC.urls.login', namespace='login')),
    path('shop/', include('TWC.urls.shop', namespace='shop')),
    path('dashboard/', include('user.urls.index', namespace='user')),
    path('products/', include('products.urls', namespace='products')), 
    path('cart/', include('cart.urls', namespace='cart')),
    path('accounts/', include('allauth.urls')),
    path('', IndexView.as_view(), name="home_view"),
    path('<str:username>', IndexView.as_view(), name='affiliate_redirect'),
    path('funnel/', ProductFunnelView.as_view(), name='product_funnel'),
    path('funnel/<str:product>/', ProductFunnelView.as_view(), name='product_funnel_with_params'),
    path('generate-funnel-username/', generate_funnel_username, name='generate_funnel_username'),
    path('funnel/create-order', create_order, name='create_order'),
    path('dummy-list/', TemplateView.as_view(template_name='dummy_list.html'), name='list'),
    re_path(r'^.*/$', Handle404View.as_view(), name='handle_404'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
