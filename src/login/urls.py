from django.urls import path
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.views import LogoutView
from .views import EcomLoginView, RegisterView

app_name = 'login'
urlpatterns = [
    path('forgot-password/', TemplateView.as_view(template_name='login/forgot-password.html'), name='forgot_password'),
    path('', EcomLoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
]