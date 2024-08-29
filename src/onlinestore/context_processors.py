# ecommerce context_processors.py

from django.contrib.auth import get_user_model

User = get_user_model()


def referrer(request):
    try:
        referrer_username = request.session.get('referrer')
        if referrer_username:
            referrer = User.objects.filter(username=referrer_username).first()
            if referrer:
                return {'referrer': referrer}
        return {'referrer': None}
    except Exception as e:
        print(f"Error in referrer context processor: {e}")
        return {'referrer': None}