from django.urls import path, include, re_path
from django.conf.urls import handler404
from django.conf.urls.static import static
from onlinestore.views import *
from ..views import EmailFormView

urlpatterns = [
    path('become-seller/', BecomeSellerView.as_view(), name="become_seller"),
    path('mail-success/', TemplateView.as_view(template_name='mail-success.html'), name="mail_success"),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name="terms"),
    path('test-email/', EmailFormView.as_view(), name="test_email"),
    path('login/', include('TWC.urls.login', namespace='login')),
    path('shop/', include('TWC.urls.shop', namespace='shop')),
    path('dashboard/', include('user.urls.index', namespace='user')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('accounts/', include('allauth.urls')),
    path('', IndexView.as_view(), name="home_view"),
    path('<str:username>', IndexView.as_view(), name='affiliate_redirect'),
    path('funnel/', ProductFunnelView.as_view(), name='product_funnel'),
    path('funnel/<str:product>/', ProductFunnelView.as_view(), name='product_funnel_with_params'),
    path('generate-funnel-username/', generate_funnel_username, name='generate_funnel_username'),
    path('funnel/create-order', create_order, name='create_order'),
    # re_path(r'^.*/$', Handle404View.as_view(), name='handle_404'),
]

handler404 = Handle404View.as_view()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
