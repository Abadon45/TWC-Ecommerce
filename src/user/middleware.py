from django.utils.deprecation import MiddlewareMixin

class APISessionAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """Simulates a logged-in user using session data from the API."""
        if request.session.get("is_authenticated"):
            request.user = type("User", (object,), {
                "username": request.session.get("username"),
                "is_authenticated": True
            })()
        else:
            request.user = type("User", (object,), {"is_authenticated": False})()
