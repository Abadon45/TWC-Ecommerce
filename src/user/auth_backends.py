from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AnonymousUser

class APIUser(AnonymousUser):
    """Temporary User Model for API Authentication"""

    def __init__(self, username, token):
        self.username = username
        self.token = token

    def __str__(self):
        return self.username

    @property
    def is_authenticated(self):
        return True  # Django expects this

    @property
    def is_anonymous(self):
        return False  # Django expects this

class APIAuthenticationBackend(BaseBackend):
    def authenticate(self, request, username=None, api_user_data=None):
        if api_user_data:
            return APIUser(username=username, token=api_user_data["token"])
        return None

    def get_user(self, user_id):
        return APIUser(username=user_id, token="")  # No real token needed