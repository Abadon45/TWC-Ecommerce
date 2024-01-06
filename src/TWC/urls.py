from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
# from cart.views import cart_detail_api_view
from ecommerce.views import Handle404View

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', TemplateView.as_view(template_name='about.html'), name="about"),
    path('become-seller/', TemplateView.as_view(template_name='become-seller.html'), name="become_seller"),
    path('coming-soon/', TemplateView.as_view(template_name='coming-soon.html'), name="coming_soon"),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name="contact"),
    path('faqs/', TemplateView.as_view(template_name='faq.html'), name="faqs"),
    path('help/', TemplateView.as_view(template_name='help.html'), name="help"),
    path('mail-success/', TemplateView.as_view(template_name='mail-success.html'), name="mail_success"),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name="privacy"),
    path('return/', TemplateView.as_view(template_name='return.html'), name="return"),
    path('team/', TemplateView.as_view(template_name='team.html'), name="team"),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name="terms"),
    path('testimonial/', TemplateView.as_view(template_name='testimonial.html'), name="testimonial"),
    path('404/', TemplateView.as_view(template_name='404.html'), name="404"),
    path('wishlist/', TemplateView.as_view(template_name='wishlist.html'), name="wishlist"),
    path('', TemplateView.as_view(template_name='index.html'), name="home_view"),
    # path('api/cart/', cart_detail_api_view, name="api_cart"),
    path('login/', include('login.urls', namespace='login')),
    path('shop/', include('shop.urls', namespace='shop')),
    path('user/', include('user.urls', namespace='user')),
    path('vendor/', include('vendor.urls', namespace='vendor')), 
    path('products/', include('products.urls', namespace='products')), 
    path('cart/', include('cart.urls', namespace='cart')), 
    re_path(r'^.*/$', Handle404View.as_view(), name='handle_404'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
