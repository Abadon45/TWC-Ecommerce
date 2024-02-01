from django.contrib.admin.sites import AdminSite
from django.shortcuts import redirect

class TWCAdminSite(AdminSite):
    def login(self, request, extra_context=None):
        response = super().login(request, extra_context)
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('/admin/')
        return response

admin_site = TWCAdminSite()