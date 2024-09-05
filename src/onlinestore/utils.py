from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

import string
import requests
import random

User = get_user_model()


def random_string_generator(size=6, chars=string.digits):
    # Generate a random 6-digit number as a string
    random_digits = ''.join(random.choice(chars) for _ in range(size))
    return f"TWC{random_digits}"

def unique_order_id_generator(instance, size=6, chars=string.digits):
    if instance:
        order_new_id = random_string_generator(size=size, chars=chars)
        Klass = instance.__class__

        # Ensure the generated order ID is unique
        while Klass.objects.filter(order_id=order_new_id).exists():
            order_new_id = random_string_generator(size=size, chars=chars)

        return order_new_id
    else:
        return random_string_generator(size=size, chars=chars)

def unique_slug_generator(instance, new_slug=None):
    """
    This assumes your instance
    has a model with an 'order_id' field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.order_id)  # Use the correct field for your model

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(order_id=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug,
            randstr=random_string_generator(size=4)
        )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def is_valid_username(username):
    try:
        User.objects.get(username=username)
        return True
    except User.DoesNotExist:
        return False


def check_sponsor_and_redirect(request, username, success_redirect_url, slug=None):
    """
    Checks the username via an external API and redirects based on the result.

    Parameters:
    - request: The original HTTP request.
    - username: The username to check.
    - success_redirect_url: The URL to redirect to if the username check is successful.
    - slug: An optional slug for URL building.

    Returns:
    - HttpResponseRedirect to the appropriate URL or HttpResponseNotFound if the check fails.
    """
    api_url = f'https://dashboard.twcako.com/account/api/check-username/{username}/'
    print(f'Username is: {username}')

    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        try:
            data = response.json()  # Attempt to parse JSON
        except ValueError:  # Handle JSON decoding errors
            return HttpResponseNotFound("Invalid JSON response from the API.")

        is_success = data.get('success')

        if is_success:
            if username == "admin":  # Handle special case for "admin"
                return HttpResponseRedirect(reverse('handle_404'))
            request.session['referrer'] = username
            print(f"Referrer: {request.session['referrer']}")
            if slug:
                return HttpResponseRedirect(reverse(success_redirect_url, kwargs={'slug': slug}))
            return HttpResponseRedirect(reverse(success_redirect_url))
        else:
            return HttpResponseRedirect(reverse('handle_404'))

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return HttpResponseNotFound("API request failed.")


def send_temporary_account_email(user, first_name, temporary_username, temporary_password):
    """
    Sends a temporary account email to the user.

    Args:
        user: The user instance to whom the email will be sent.
        first_name: First name of the user.
        temporary_username: The temporary username generated for the user.
        temporary_password: The temporary password generated for the user.

    Returns:
        None
    """
    subject = 'TWC Online Store Temporary Account'
    message = (f'Good Day {first_name},\n\n\nYou have successfully registered an account on TWConline.store!!'
               f'\n\n\nHere are your temporary account details:\n\n'
               f'Username: {temporary_username}\nPassword: {temporary_password}\n\n\nThank you for your order!')
    from_email = settings.EMAIL_MAIN
    recipient_list = [user.email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")