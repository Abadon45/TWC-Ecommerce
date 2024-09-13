# ecommerce context_processors.py

from django.contrib.auth import get_user_model

User = get_user_model()


def referrer(request):
    try:
        referrer = request.session['messenger_link']
        if referrer:
            return {'referrer': referrer}
        return {'referrer': None}
    except Exception as e:
        print(f"Error in referrer context processor: {e}")
        return {'referrer': None}