from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .views import *
from django.urls import reverse_lazy

app_name = 'login'
urlpatterns = [
    path('password-reset/', ForgotPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='login/password_reset_confirm.html',
            success_url=reverse_lazy('login:password_reset_complete')),
            name='password_reset_confirm'),
    path('password-reset-complete/', PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('password-done/', PasswordDoneView.as_view(), name='password_done'),
    path('', EcomLoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
]