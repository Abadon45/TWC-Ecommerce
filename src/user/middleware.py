from django.utils.deprecation import MiddlewareMixin

class APISessionAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """Simulates a logged-in user using session data from the API."""
        is_authenticated = request.session.get("is_authenticated", False)
        username = request.session.get("username", "")

        request.user = type("User", (object,), {
            "username": username,
            "is_authenticated": is_authenticated
        })()
