# ecommerce context_processors.py

from django.contrib.auth import get_user_model

User = get_user_model()


def referrer(request):
    try:
        referrer_username = request.session['referrer']
        referrer = User.objects.get(username=referrer_username)
        print(f'Referrer: {referrer}')
        
        return {'referrer': referrer}
    except Exception as e:
        print(f"Error in referrer: {e}")
        return {'referrer': ""}