
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from user.views import DashboardView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name='user'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    
    # path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(success_url=reverse_lazy('account:password_change_done')), name='password_change_done'),
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)