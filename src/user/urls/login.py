from django.urls import path
from user.views import *


app_name = 'login'
urlpatterns = [
    path("", APILoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
]
