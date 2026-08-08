from collections import defaultdict

import requests

from django.contrib.auth import get_user_model
from django.http import HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from urllib.parse import urlparse

from django.views.decorators.http import require_GET

User = get_user_model()



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
        response = requests.get(api_url, verify=False)
        response.raise_for_status()  # Raise an exception for HTTP errors

        try:
            data = response.json()  # Attempt to parse JSON
        except ValueError:  # Handle JSON decoding errors
            return HttpResponseNotFound("Invalid JSON response from the API.")

        is_success = data.get('success')
        messenger_link = data.get('messenger_link')
        mobile = data.get('mobile')
        print(f'messenger_link: {messenger_link}')

        if is_success:
            if username == "admin":  # Handle special case for "admin"
                return HttpResponseRedirect(reverse('handle_404'))
            request.session['referrer'] = username
            request.session['messenger_link'] = messenger_link
            request.session['mobile'] = mobile

            print(f"Session Referrer Set: {request.session['referrer']}")
            request.session.modified = True

            if slug:
                return HttpResponseRedirect(reverse(success_redirect_url, kwargs={'slug': slug}))
            return HttpResponseRedirect(reverse(success_redirect_url))
        else:
            return HttpResponseRedirect(reverse('handle_404'))

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return HttpResponseNotFound("API request failed.")


def send_temporary_account_email(user, full_name, temporary_username, temporary_password):
    """
    Sends a temporary account email to the user.

    Args:
        user: The user instance to whom the email will be sent.
        full_name: First name of the user.
        temporary_username: The temporary username generated for the user.
        temporary_password: The temporary password generated for the user.

    Returns:
        None
    """
    subject = 'TWC Online Store Temporary Account'
    message = (f'Good Day {full_name},\n\n\nYou have successfully registered an account on TWConline.store!!'
               f'\n\n\nHere are your temporary account details:\n\n'
               f'Username: {temporary_username}\nPassword: {temporary_password}\n\n\nThank you for your order!')
    from_email = settings.EMAIL_MAIN
    recipient_list = [user.email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


def fetch_address_data(request):
    address_api_url = getattr(settings, 'ADDRESS_API_URL', 'https://dashboard.twcako.com/addresses/api/get-address/')

    try:
        # Fetch address data from the external API
        response = requests.get(address_api_url, verify=False, timeout=10)
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data, safe=False)
    except requests.exceptions.RequestException as e:
        # Handle error gracefully
        print(f"Failed to fetch address data: {e}")
        return JsonResponse({'error': 'Failed to fetch address data'}, status=500)


@require_GET
def fetch_category_count(request):
    # API URL to fetch product data
    api_url = settings.SHOP_PRODUCTS_API

    try:
        # Fetch filtered data from the API
        response = requests.get(api_url, verify=False, timeout=10)
        response.raise_for_status()

        # Check if the response is successful and print the data
        data = response.json()

        if not data.get("success"):
            print("API response does not indicate success.")
            return JsonResponse({'category_product_count': {}})

        # Extract products from the API response
        queryset = data.get("products", [])
        print(f"Fetched {len(queryset)} products.")  # Debugging: check how many products are fetched

        # Create a dictionary to store product counts per category (cat1 -> cat2 -> count)
        category_product_count = defaultdict(lambda: defaultdict(int))

        # Count products by cat1 (category_1) and cat2 (category_2)
        for product in queryset:
            cat1 = product.get("category_1", "all")  # Default to "all" if no category_1 is provided
            cat2 = product.get("category_2", "uncategorized")  # Default to "uncategorized" if no category_2 is provided

            # Debugging: check the categories being processed
            print(f"Processing product: category_1 = {cat1}, category_2 = {cat2}")

            category_product_count[cat1][cat2] += 1
            category_product_count['all'][cat2] += 1

        # Debugging: print the final product count structure
        print("Category Product Count:", dict(category_product_count))

        return JsonResponse({'category_product_count': category_product_count})

    except requests.exceptions.RequestException as e:
        # Handle errors if the API request fails
        print(f"Error fetching product data: {e}")
        return JsonResponse({'category_product_count': {}})



def fetch_ph_number_prefixes(api_url):
    """
    Fetch Philippine mobile number prefixes from the API.

    Args:
        api_url (str): The URL of the PHNumberPrefixes API.

    Returns:
        list: A list of prefixes, or an empty list if the API call fails.
    """
    try:
        response = requests.get(api_url, verify=False, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP status codes 4xx/5xx
        data = response.json()
        return data.get('ph_number_prefixes', [])
    except requests.RequestException as e:
        # Log the error if needed
        print(f"Error fetching prefixes: {e}")
        return []


def extract_username_from_request(request):
    """
    Extract the username (subdomain) from the request object.

    Args:
        request (HttpRequest): Django HttpRequest object.

    Returns:
        str: The subdomain (username) if found, else None.
    """
    host = request.get_host()
    domain_parts = host.split('.')

    # Assuming the subdomain is the first part of the domain
    if len(domain_parts) > 2:
        return domain_parts[0]

    return None


def fetch_vw_inventory(request):
    """
    Fetches the VW Inventory for a given username from the API.

    Args:
        request (HttpRequest): Django HttpRequest object.

    Returns:
        dict: A dictionary containing the quantity of each product and the grand total.
        None: If the request fails or no data is available.
    """
    username = extract_username_from_request(request)
    url = settings.VW_INVENTORY_API.format(username=username)

    print(f'PRODUCT FUNNEL URL: {url}')

    try:
        # Make the API call
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get('success'):
            return {
                'quantity_dict': data.get('quantity_dict', {}),
                'grand_total': data.get('grand_total', 0),
            }
        else:
            print(f"API responded with an error: {data.get('error', 'Unknown error')}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching VW inventory: {e}")
        return None