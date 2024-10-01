from django.http import HttpResponseRedirect
from django.conf import settings

def www_root_redirect(request, path=None):
    print(path)
    
    if settings.DEBUG:
        # If in development, redirect to the local host
        return HttpResponseRedirect('http://127.0.0.1:8000/')
    else:
        # If in production, redirect to the online host
        return HttpResponseRedirect('https://www.twconline.com/')