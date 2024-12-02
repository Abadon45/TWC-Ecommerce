import random
import string
import requests

from datetime import datetime
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from requests.auth import HTTPBasicAuth

from onlinestore.models import *


def sf_calculator(province=None, qty=0):
    qty = int(qty)

    ncr = {"NCR, CITY OF MANILA, FIRST DISTRICT", "CITY OF MANILA", "NCR, SECOND DISTRICT", "NCR, THIRD DISTRICT",
           "NCR, FOURTH DISTRICT"}
    luzon = {
        "ILOCOS NORTE", "ILOCOS SUR", "LA UNION", "PANGASINAN", "BATANES", "CAGAYAN", "ISABELA", "NUEVA VIZCAYA",
        "QUIRINO", "BATAAN", "BULACAN", "NUEVA ECIJA", "PAMPANGA", "TARLAC", "ZAMBALES", "AURORA", "BATANGAS",
        "CAVITE", "LAGUNA", "QUEZON", "RIZAL", "MARINDUQUE", "OCCIDENTAL MINDORO", "ORIENTAL MINDORO",
        "PALAWAN", "ROMBLON", "ABRA", "BENGUET", "IFUGAO", "KALINGA", "MOUNTAIN PROVINCE", "APAYAO"
    }
    visayas = {
        "AKLAN", "ANTIQUE", "CAPIZ", "ILOILO", "NEGROS OCCIDENTAL", "GUIMARAS", "BOHOL", "CEBU",
        "NEGROS ORIENTAL", "SIQUIJOR", "EASTERN SAMAR", "LEYTE", "NORTHERN SAMAR", "SAMAR (WESTERN SAMAR)",
        "SOUTHERN LEYTE", "BILIRAN"
    }
    mindanao = {
        "ZAMBOANGA DEL NORTE", "ZAMBOANGA DEL SUR", "ZAMBOANGA SIBUGAY", "CITY OF ISABELA", "BUKIDNON", "CAMIGUIN",
        "LANAO DEL NORTE", "MISAMIS OCCIDENTAL", "MISAMIS ORIENTAL", "DAVAO DEL NORTE", "DAVAO DEL SUR",
        "DAVAO ORIENTAL", "COMPOSTELA VALLEY", "DAVAO OCCIDENTAL", "COTABATO (NORTH COTABATO)", "SOUTH COTABATO",
        "SULTAN KUDARAT", "SARANGANI", "COTABATO CITY", "BASILAN", "LANAO DEL SUR", "MAGUINDANAO", "SULU",
        "TAWI-TAWI", "AGUSAN DEL NORTE", "AGUSAN DEL SUR", "SURIGAO DEL NORTE", "SURIGAO DEL SUR", "DINAGAT ISLANDS"
    }

    if province in ncr:
        region = "ncr"
    elif province in luzon:
        region = "luzon"
    elif province in visayas:
        region = "visayas"
    elif province in mindanao:
        region = "mindanao"
    else:
        region = None

    shipping_fees = {
        "ncr": {(0, 2): 100.00, (3, 4): 120.00, (5, 6): 160.00, (7, 8): 180.00, (9, 15): 300.00, (16, 20): 420.00,
                (20, 27): 580.00},
        "luzon": {(0, 2): 160.00, (3, 4): 180.00, (5, 6): 240.00, (7, 8): 260.00, (9, 15): 380.00, (16, 20): 500.00,
                  (20, 27): 660.00},
        "visayas": {(0, 2): 180.00, (3, 4): 200.00, (5, 6): 260.00, (7, 8): 280.00, (9, 15): 400.00, (16, 20): 520.00,
                    (20, 27): 680.00},
        "mindanao": {(0, 2): 200.00, (3, 4): 220.00, (5, 6): 280.00, (7, 8): 300.00, (9, 15): 420.00, (16, 20): 540.00,
                     (20, 27): 700.00}
    }

    if region in shipping_fees:
        for (start, end), fee in shipping_fees[region].items():
            if start <= qty <= end:
                return fee

    return 0.00


def detect_region(province):
    # Define mappings of provinces to regions
    ncr = {"NCR, CITY OF MANILA, FIRST DISTRICT", "CITY OF MANILA", "NCR, SECOND DISTRICT", "NCR, THIRD DISTRICT",
           "NCR, FOURTH DISTRICT"}
    luzon = {
        "ILOCOS NORTE", "ILOCOS SUR", "LA UNION", "PANGASINAN", "BATANES", "CAGAYAN", "ISABELA", "NUEVA VIZCAYA",
        "QUIRINO", "BATAAN", "BULACAN", "NUEVA ECIJA", "PAMPANGA", "TARLAC", "ZAMBALES", "AURORA", "BATANGAS",
        "CAVITE", "LAGUNA", "QUEZON", "RIZAL", "MARINDUQUE", "OCCIDENTAL MINDORO", "ORIENTAL MINDORO",
        "PALAWAN", "ROMBLON", "ABRA", "BENGUET", "IFUGAO", "KALINGA", "MOUNTAIN PROVINCE", "APAYAO"
    }
    visayas = {
        "AKLAN", "ANTIQUE", "CAPIZ", "ILOILO", "NEGROS OCCIDENTAL", "GUIMARAS", "BOHOL", "CEBU",
        "NEGROS ORIENTAL", "SIQUIJOR", "EASTERN SAMAR", "LEYTE", "NORTHERN SAMAR", "SAMAR (WESTERN SAMAR)",
        "SOUTHERN LEYTE", "BILIRAN"
    }
    mindanao = {
        "ZAMBOANGA DEL NORTE", "ZAMBOANGA DEL SUR", "ZAMBOANGA SIBUGAY", "CITY OF ISABELA", "BUKIDNON", "CAMIGUIN",
        "LANAO DEL NORTE", "MISAMIS OCCIDENTAL", "MISAMIS ORIENTAL", "DAVAO DEL NORTE", "DAVAO DEL SUR",
        "DAVAO ORIENTAL", "COMPOSTELA VALLEY", "DAVAO OCCIDENTAL", "COTABATO (NORTH COTABATO)", "SOUTH COTABATO",
        "SULTAN KUDARAT", "SARANGANI", "COTABATO CITY", "BASILAN", "LANAO DEL SUR", "MAGUINDANAO", "SULU",
        "TAWI-TAWI", "AGUSAN DEL NORTE", "AGUSAN DEL SUR", "SURIGAO DEL NORTE", "SURIGAO DEL SUR", "DINAGAT ISLANDS"
    }

    # Check the province against each region mapping
    if province in ncr:
        return "ncr"
    elif province in luzon:
        return "luzon"
    elif province in visayas:
        return "visayas"
    elif province in mindanao:
        return "mindanao"
    else:
        return "unknown"



def split_full_name(full_name):
    # Common last name prefixes in some languages
    last_name_prefixes = {"de", "de la", "van", "von", "da", "del", "la", "san", "dela"}

    parts = full_name.strip().split()

    if len(parts) <= 1:
        return full_name, None

    first_name = []
    last_name = []

    # Reverse through the name parts to detect last name prefixes
    for i in range(len(parts) - 1, -1, -1):
        if ' '.join(parts[i:]).lower() in last_name_prefixes or not last_name:
            # Add part to last name (to be joined later in correct order)
            last_name.insert(0, parts[i])
        else:
            # Add remaining parts to first name
            first_name = parts[:i + 1]
            break

    # Join the first and last names into strings
    first_name = ' '.join(first_name) if first_name else parts[0]
    last_name = ' '.join(last_name) if last_name else None

    return first_name, last_name


def generate_invoice_number():
    # Get the current date and time in the specified format
    date_time_str = datetime.now().strftime("%y%m%d%H%M%S")
    # Generate 3 random alphanumeric characters
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    # Combine date, time, and random characters
    invoice_number = f"{date_time_str}{random_chars}"
    return invoice_number

def get_xendit_api_key(request):
    """
    Determines the appropriate Xendit API key based on the root domain of the request.

    Returns:
        str: The appropriate Xendit API key (live or test).
    """
    # Extract the root domain from the request host
    domain = request.get_host().split('.')
    root_domain = '.'.join(domain[-2:])  # Get the last two parts of the domain
    print(f"Current Domain: {root_domain}")

    # Determine which API key to return based on the root domain
    if root_domain == 'twconline.store':
        return settings.XENDIT_API_KEY  # Use live API key
    else:
        return settings.XENDIT_TEST_API  # Use test API key


def check_xendit_invoice_status(request, invoice_id):

    xendit_url = f"https://api.xendit.co/v2/invoices/{invoice_id}"
    api_key = get_xendit_api_key(request)

    try:
        response = requests.get(xendit_url, auth=HTTPBasicAuth(api_key, ''))
        response.raise_for_status()

        if response.status_code == 200:
            invoice_data = response.json()
            status = invoice_data.get('status')

            if status == 'PAID':
                print(f"Invoice {invoice_id} has been paid. Payment approved.")
                return 'PAID'
            elif status == 'UNPAID':
                print(f"Invoice {invoice_id} is still pending.")
                return 'UNPAID'
            else:
                print(f"Invoice {invoice_id} status is {status}.")
                return status
        else:
            print(f"Failed to fetch invoice status. HTTP Status Code: {response.status_code}")
            print(f"Error Response: {response.json()}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Exception occurred: {str(e)}")
        return None


def get_access_token():
    """Fetches a fresh access token for API calls."""
    url = 'https://dashboard.twcako.com/order/api/get-access-token/'
    data = {
        "refresh": settings.REFRESH_TOKEN
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()

        if response.status_code == 200 and "access_token" in response.json():
            return response.json().get("access_token")

    except requests.exceptions.RequestException as e:
        print("Error fetching access token:", e)
        # Log the error details for debugging purposes
        return None


def submit_checkout_base(request, redirect_url):
    referrer_username = request.GET.get('username')
    payment_method = request.GET.get('payment_method', 'Cash On Delivery')
    ordered_items_by_shop = request.session.get('ordered_items_by_shop', {})
    address_from_session = request.session.get('shipping_address', {})

    customer_name = address_from_session.get('full_name')
    customer_phone = address_from_session.get('phone')

    shipping_amount = float(SiteSetting.get_fixed_shipping_fee())

    request.session['payment_method'] = payment_method
    print(f'Payment Method: {payment_method}')

    if 'referrer' not in request.session:
        request.session['referrer'] = referrer_username

    # Prepare ordered items list
    items = []
    total_discount = 0
    shop_count = 0
    invoice_number = generate_invoice_number()
    request.session['invoice_number'] = invoice_number

    for shop, shop_data in ordered_items_by_shop.items():
        shop_count += 1
        discount_price = float(shop_data.get('discount', 0))
        total_discount += discount_price
        for item in shop_data['items']:
            items.append({
                "name": item['product']['name'],
                "quantity": item['quantity'],
                "price": float(item['product']['price']),
            })

    if referrer_username:
        referrer_data = validate_referrer(referrer_username)

        if not referrer_data['success']:
            return JsonResponse(referrer_data, status=400)

    # Prepare the redirect URL
    redirect_to_create_order = reverse('cart:create_order')

    # If COD, create the order directly
    if payment_method == 'Cash On Delivery':
        request.session['checkout_completed'] = True
        return HttpResponseRedirect(reverse('cart:create_order'))

    # If Xendit, prepare for invoice creation
    elif payment_method.lower() == 'xendit':
        request.session['checkout_completed'] = True
        customer = create_or_get_xendit_customer(customer_name, customer_phone)
        success_redirect_url = request.build_absolute_uri(redirect_to_create_order)
        failure_redirect_url = request.build_absolute_uri(reverse('cart:cart'))

        return create_xendit_invoice(
            request,
            customer_name=customer_name,
            customer_phone=customer_phone,
            items=items,
            shipping_amount=shipping_amount,
            unique_invoice_id=invoice_number,
            success_redirect_url=success_redirect_url,
            failure_redirect_url=failure_redirect_url,
            shop_count=len(ordered_items_by_shop),
            total_discount=total_discount
        )

    return redirect('cart:cart')


def validate_referrer(referrer_username):
    if referrer_username == 'admin':
        return {'success': True}  # Skip admin validation

    # Define API URL
    api_url = f'https://dashboard.twcako.com/account/api/check-username/{referrer_username}/'

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, dict):
            raise ValueError("API response is not a valid JSON object")

        # If validation fails, return a failure response
        if not data.get('success'):
            return {'success': False, 'error': 'Referrer username does not exist'}

        # Otherwise, return referrer details for session handling
        return {
            'success': True,
            'messenger_link': data.get('messenger_link'),
            'sponsor_mobile': data.get('mobile')
        }

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return {'success': False, 'error': 'Failed to check referrer username'}
    except ValueError as e:
        print(f"Error parsing response: {e}")
        return {'success': False, 'error': 'Invalid API response'}


def create_xendit_invoice(
        request, customer_name, customer_phone,
        items, shipping_amount, unique_invoice_id,
        success_redirect_url, failure_redirect_url, shop_count, total_discount):
    # Xendit API URL for creating an invoice
    xendit_url = "https://api.xendit.co/v2/invoices"

    # Calculate total amount from items
    total_amount = sum(item["quantity"] * item["price"] for item in items)

    # Subtract the total discount from the total amount
    total_amount -= total_discount

    # Ensure total amount doesn't go below 0
    if total_amount < 0:
        total_amount = 0

    # Create invoice items for the payload
    invoice_items = [
        {
            "name": item["name"],
            "quantity": item["quantity"],
            "price": item["price"]
        }
        for item in items
    ]

    invoice_items.append({
        "name": "Shipping Cost",  # For all shops
        "quantity": shop_count,  # Number of shops in the order
        "price": shipping_amount * shop_count,  # Fixed shipping fee per shop
        "description": f"Flat rate shipping fee for {shop_count} shop(s)"
    })

    # Update the total amount to include shipping costs
    total_amount += shipping_amount * shop_count

    # unique_invoice_id_str = ", ".join(unique_invoice_id)
    unique_invoice_id_str = unique_invoice_id

    # Invoice data that will be sent to Xendit API
    payload = {
        "external_id": unique_invoice_id_str,
        "description": "TWC Online Store Payment",
        "amount": total_amount,
        "success_redirect_url": success_redirect_url,
        "failure_redirect_url": failure_redirect_url,
        "items": invoice_items,
        "customer": {
            "given_names": customer_name,
            "mobile_number": customer_phone,
        }
    }

    print(f'Payload: {payload}')

    api_key = get_xendit_api_key(request)

    try:

        # Send the POST request to Xendit API
        response = requests.post(
            xendit_url,
            json=payload,
            auth=(api_key, '')  # Xendit API uses basic auth with just the API key and empty password
        )

        if response.status_code == 200:
            invoice_data = response.json()

            print(f'Invoice Data: {invoice_data}')

            invoice_url = invoice_data['invoice_url']
            invoice_id = invoice_data['id']
            request.session['invoice_id'] = invoice_id
            print(f'Redirecting to Xendit Invoice URL: {invoice_url}')  # Debugging log
            return JsonResponse({'redirect_url': invoice_url})
            # return HttpResponseRedirect(invoice_url)
        else:
            print(f'Error response from Xendit: {response.json()}')  # Debugging log
            return JsonResponse({"status": "error", "message": response.json()}, status=response.status_code)

    except requests.exceptions.RequestException as e:
        print(f'Exception occurred: {str(e)}')  # Debugging log
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def create_or_get_xendit_customer(customer_name, customer_phone):
    api_key = settings.XENDIT_API_KEY

    # Construct reference_id based on name
    reference_id = f"customer-{customer_name}"

    # Xendit API URL to search for customers
    xendit_search_url = f"https://api.xendit.co/customers?reference_id={reference_id}"

    try:
        # Try to get the customer from Xendit
        search_response = requests.get(
            xendit_search_url,
            auth=(api_key, '')
        )

        if search_response.status_code == 200:
            customers = search_response.json().get('data', [])
            print(f"Search response: {customers}")  # Debugging: check the full response

            if customers:
                print("Customer already exists, skipping creation.")
                return None
            else:
                print("New Customer!!!")

        else:
            print(f"Error fetching customer or customer does not exist: {search_response.json()}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Exception occurred while fetching customer: {str(e)}")
        return None

    # If customer is not found, create a new one
    xendit_create_url = "https://api.xendit.co/customers"

    customer_payload = {
        "reference_id": reference_id,
        "type": "INDIVIDUAL",
        "individual_detail": {
            "given_names": customer_name,
        },
        "mobile_number": customer_phone,
    }

    try:
        create_response = requests.post(
            xendit_create_url,
            json=customer_payload,
            auth=(api_key, '')
        )

        if create_response.status_code == 200:
            print(f"Customer created successfully: {create_response.json()}")
            return create_response.json()  # Return newly created customer data
        else:
            print(f"Error creating customer: {create_response.json()}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Exception occurred: {str(e)}")
        return None


def create_order(request):
    """
    Creates an order by sending a request to the TWC Ako API.
    """
    order_url = 'https://dashboard.twcako.com/order/api/create-order/'
    access_token = get_access_token()
    ordered_items_by_shop = request.session.get('ordered_items_by_shop', {})
    address_from_session = request.session.get('shipping_address', {})
    redirect_url = request.session.get('redirect_url', None)

    # invoice_id = request.session.get('invoice_id', None)
    # status = check_xendit_invoice_status(request, invoice_id)
    # print(f'Invoice ID: {invoice_id}')
    # print(f'xendit status: {status}')


    payment_method = request.session.get('payment_method')
    if payment_method == 'Cash On Delivery':
        payment_method = 'cod'

    print(f'Redirect URL: {redirect_url}')
    print(f'Ordered Items by Shop: {ordered_items_by_shop}')
    print(f'Shipping Address from Session: {address_from_session}')

    full_name = address_from_session.get('full_name')
    first_name, last_name = split_full_name(full_name)

    # Prepare the shipping details for the order
    shipping_details = {
        "name": first_name,
        "last_name": last_name,
        "mobile": address_from_session.get('phone'),
        "address": address_from_session.get('address'),
        "barangay": address_from_session.get('barangay'),
        "city": address_from_session.get('city'),
        "province": address_from_session.get('province'),
        "country": 'Philippines',
        "postal_code": address_from_session.get('postcode'),
        "shipping_notes": address_from_session.get('message', "")
    }

    # Order creation logic remains the same
    for shop, shop_data in ordered_items_by_shop.items():
        cart_items = []
        shop_total_barley_point = 0

        for item in shop_data['items']:
            product_name = item['product']['name']
            barley_point = item['product'].get('barley_point', 0)
            quantity = item.get('quantity', 1)

            # Debugging to check individual values
            print(f"Product: {product_name}, Barley Point: {barley_point}, Quantity: {quantity}")

            # Multiply the barley point by the quantity and add to total
            shop_total_barley_point += barley_point * quantity
            cart_items.append({
                'sku': item['product']['id'],
                'qty': item['quantity'],
            })

        cod_amount = ordered_items_by_shop[shop]['cod_amount']
        discount_price = ordered_items_by_shop[shop].get('discount', 0)
        invoice_number = request.session.get('invoice_number', "")
        print(f'Shop in create order: {shop}')
        print(f'Total Barley Point: {shop_total_barley_point} for shop: {shop}')
        print(f'Invoice Number in Create Order: {invoice_number}')

        const_data = {
            "username": request.session['referrer'],
            "shipping_details": shipping_details,
            "order_details": {
                "cod_amount": cod_amount,
                "discount_price": discount_price,
                "payment_method": payment_method,
            },
            "cart_items": cart_items,
            "barley_point": shop_total_barley_point,
            "invoice_number": invoice_number,
        }

        print(f'const_data: {const_data}')

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        response = requests.post(order_url, json=const_data, headers=headers)

        # Log the response status code and content
        print(f'POST {order_url} - Status Code: {response.status_code}, Response: {response.text}')

        if response.status_code == 401:
            print("Authentication failed. Please check the token or credentials.")
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")

        if response.status_code == 201:
            print("Order created successfully:", response.json())
            order_data = response.json()  # Get the order data from the response
            order_number = order_data.get('order_number')

            print(f"Order number set in session: {order_number}")

            ordered_items_by_shop[shop]['order_number'] = order_number
        else:
            print("Error creating order:", response.status_code, response.text)
            return HttpResponseRedirect(reverse('cart:cart'))

    if 'promo' in ordered_items_by_shop:
        redirect_url = reverse('cart:promo_checkout_done')

    # Save order details to session
    request.session['ordered_items_by_shop'] = ordered_items_by_shop
    request.session['order_complete'] = True
    # Ensure redirect_url is properly used for redirection
    print(f'Redirecting to: {redirect_url if redirect_url else "cart"}')
    if redirect_url:
        return HttpResponseRedirect(redirect_url)
    else:
        # Fallback redirect if redirect_url is not set
        return HttpResponseRedirect(reverse('cart:cart'))
