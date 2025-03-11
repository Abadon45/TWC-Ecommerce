from django.urls import path, include
from onlinestore.views import *
from user.views import APILoginView

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
    path("user/", include("TWC.urls.dashboard", namespace="dashboard")),
    # path("login/", APILoginView.as_view(), name="login"),
    path('shop/', include('TWC.urls.shop', namespace='shop')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('accounts/', include('allauth.urls')),
    path('', IndexView.as_view(), name="home_view"),
    path('pf/', ProductFunnelView.as_view(), name='product_funnel'),
    path('pf-vw/<str:product>/', ProductFunnelView.as_view(), name='product_funnel_vw'),
    path('pf-ds/<str:product>/', ProductFunnelView.as_view(), name='product_funnel_ds'),
    path('pf/create-order', create_order, name='create_order'),

]

handler404 = Handle404View.as_view()


