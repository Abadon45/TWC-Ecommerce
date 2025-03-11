from django.urls import path, include

from user.views import *
from django.urls import reverse_lazy

app_name = 'login'
urlpatterns = [
    path("user/", include("user.urls.login", namespace="login")),
]
