import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

from onlinestore.models import *


def sf_calculator(region=None, qty=0):
    qty = int(qty)

    ncr = {"NATIONAL CAPITAL REGION (NCR)"}
    luzon = {
        "REGION I (ILOCOS REGION)",
        "REGION II (CAGAYAN VALLEY)",
        "REGION III (CENTRAL LUZON)",
        "REGION IV-A (CALABARZON)",
        "REGION V (BICOL REGION)",
        "REGION IV-B (MIMAROPA)",
        "CORDILLERA ADMINISTRATIVE REGION (CAR)"
    }
    visayas = {
        "REGION VI (WESTERN VISAYAS)",
        "REGION VII (CENTRAL VISAYAS)",
        "REGION VIII (EASTERN VISAYAS)"
    }
    mindanao = {
        "REGION IX (ZAMBOANGA PENINSULA)",
        "REGION X (NORTHERN MINDANAO)",
        "REGION XI (DAVAO REGION)",
        "REGION XII (SOCCSKSARGEN)",
        "AUTONOMOUS REGION IN MUSLIM MINDANAO (ARMM)",
        "REGION XIII (Caraga)"
    }

    if region in ncr:
        region = "ncr"
    elif region in luzon:
        region = "luzon"
    elif region in visayas:
        region = "visayas"
    elif region in mindanao:
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


def detect_region(region):
    ncr = {"NATIONAL CAPITAL REGION (NCR)"}
    luzon = {
        "REGION I (ILOCOS REGION)",
        "REGION II (CAGAYAN VALLEY)",
        "REGION III (CENTRAL LUZON)",
        "REGION IV-A (CALABARZON)",
        "REGION V (BICOL REGION)",
        "REGION IV-B (MIMAROPA)",
        "CORDILLERA ADMINISTRATIVE REGION (CAR)"
    }
    visayas = {
        "REGION VI (WESTERN VISAYAS)",
        "REGION VII (CENTRAL VISAYAS)",
        "REGION VIII (EASTERN VISAYAS)"
    }
    mindanao = {
        "REGION IX (ZAMBOANGA PENINSULA)",
        "REGION X (NORTHERN MINDANAO)",
        "REGION XI (DAVAO REGION)",
        "REGION XII (SOCCSKSARGEN)",
        "AUTONOMOUS REGION IN MUSLIM MINDANAO (ARMM)",
        "REGION XIII (Caraga)"
    }

    if region in ncr:
        return "ncr"
    elif region in luzon:
        return "luzon"
    elif region in visayas:
        return "visayas"
    elif region in mindanao:
        return "mindanao"
    else:
        return "unknown"


def get_access_token():
    """Fetches a fresh access token for API calls."""
    token_data = {"refresh": settings.RESPONSE_TOKEN}
    headers = {'Content-Type': 'application/json'}
    response = requests.post('https://dashboard.twcako.com/order/api/token/refresh/', json=token_data, headers=headers)
    response.raise_for_status()
    return response.json().get('access')


def submit_checkout_base(request, redirect_url):
    access_token = get_access_token()
    payment_method = request.GET.get('payment_method', 'Cash On Delivery')
    ordered_items_by_shop = request.session.get('ordered_items_by_shop', {})
    address_from_session = request.session.get('shipping_address', {})
    customer_email = address_from_session.get('email')
    customer_name = f"{address_from_session.get('first_name')} {address_from_session.get('last_name')}"
    customer_phone = address_from_session.get('phone')
    shipping_amount = float(SiteSetting.get_fixed_shipping_fee())

    # Prepare the shipping details for the order
    shipping_details = {
        "first_name": address_from_session.get('first_name'),
        "last_name": address_from_session.get('last_name'),
        "mobile": customer_phone,
        "address": address_from_session.get('line1'),
        "barangay": address_from_session.get('barangay'),
        "region": address_from_session.get('region'),
        "city": address_from_session.get('city'),
        "province": address_from_session.get('province'),
        "country": 'Philippines',
        "postal_code": address_from_session.get('postcode'),
        "shipping_notes": address_from_session.get('message', "")
    }

    # If COD, create the order directly
    if payment_method.lower() == 'cash on delivery':
        unique_invoice_ids = create_order(
            request,
            referrer=request.session.get('referrer'),
            shipping_details=shipping_details,
            payment_method=payment_method,
            items=request.session.get('ordered_items', []),
            discount_price=request.session.get('total_discount', 0),
            access_token=access_token
        )
        if unique_invoice_ids:
            return redirect(redirect_url)
        return redirect('cart:cart')  # On failure

    # If Xendit, prepare for invoice creation
    elif payment_method.lower() == 'xendit':
        customer = create_or_get_xendit_customer(customer_name, customer_email, customer_phone)
        success_redirect_url = request.build_absolute_uri(reverse('cart:checkout_complete'))
        failure_redirect_url = request.build_absolute_uri(reverse('cart:cart'))

        return create_xendit_invoice(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            items=[
                {"name": item['product']['name'], "quantity": item['quantity'],
                 "price": float(item['product']['price'])}
                for shop, shop_data in ordered_items_by_shop.items() for item in shop_data['items']
            ],
            shipping_amount=shipping_amount,
            unique_invoice_id=[],
            success_redirect_url=success_redirect_url,
            failure_redirect_url=failure_redirect_url,
            shop_count=len(ordered_items_by_shop),
            total_discount=request.session.get('total_discount', 0)
        )

    return redirect('cart:cart')


def create_xendit_invoice(
        customer_name, customer_email, customer_phone,
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

    unique_invoice_id_str = ", ".join(unique_invoice_id)

    # Invoice data that will be sent to Xendit API
    payload = {
        "external_id": unique_invoice_id_str,  # Pass the unique invoice ID
        "payer_email": customer_email,  # Customer email
        "description": "TWC Online Store Payment",  # Description of the payment
        "amount": total_amount,  # Total amount in IDR
        "success_redirect_url": success_redirect_url,
        "failure_redirect_url": failure_redirect_url,
        "items": invoice_items,  # List of items in the invoice
        "customer": {
            "given_names": customer_name,
            "email": customer_email,
            "mobile_number": customer_phone,
        }
    }

    print(f'Payload: {payload}')

    # Xendit API key from settings
    api_key = settings.XENDIT_API_KEY

    try:
        # Send the POST request to Xendit API
        response = requests.post(
            xendit_url,
            json=payload,
            auth=(api_key, '')  # Xendit API uses basic auth with just the API key and empty password
        )

        # Check if the request was successful
        if response.status_code == 200:
            invoice_data = response.json()
            invoice_url = invoice_data['invoice_url']
            print(f'Redirecting to Xendit Invoice URL: {invoice_url}')  # Debugging log
            return JsonResponse({'redirect_url': invoice_url})
            # return HttpResponseRedirect(invoice_url)
        else:
            print(f'Error response from Xendit: {response.json()}')  # Debugging log
            return JsonResponse({"status": "error", "message": response.json()}, status=response.status_code)

    except requests.exceptions.RequestException as e:
        print(f'Exception occurred: {str(e)}')  # Debugging log
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def create_or_get_xendit_customer(customer_name, customer_email, customer_phone):
    api_key = settings.XENDIT_API_KEY

    # Construct reference_id based on email
    reference_id = f"customer-{customer_email}"

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
        "reference_id": f"customer-{customer_email}",
        "type": "INDIVIDUAL",
        "individual_detail": {
            "given_names": customer_name,
        },
        "email": customer_email,
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


def create_order(request, referrer, shipping_details, payment_method, items, discount_price, access_token):
    """
    Creates an order by sending a request to the TWC Ako API.
    """
    order_url = 'https://dashboard.twcako.com/order/api/create-order/'
    ordered_items_by_shop = request.session.get('ordered_items_by_shop', {})
    unique_invoice_ids = []

    for shop, shop_data in ordered_items_by_shop.items():
        shop_total_barley_point = sum(
            item['product'].get('barley_point', 0) * item['quantity']
            for item in shop_data['items']
        )

        cart_items = [
            {'sku': item['product']['id'], 'qty': item['quantity']}
            for item in shop_data['items']
        ]

        order_data = {
            "username": referrer,
            "shipping_details": shipping_details,
            "order_details": {
                "cod_amount": shop_data['cod_amount'],
                "discount_price": discount_price,
                "payment_method": payment_method,
            },
            "cart_items": cart_items,
            "barley_point": shop_total_barley_point,
        }

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        response = requests.post(order_url, json=order_data, headers=headers)

        if response.status_code == 201:
            order_response = response.json()
            order_number = order_response.get('order_number')
            unique_invoice_ids.append(order_number)
            ordered_items_by_shop[shop]['order_number'] = order_number
        else:
            print(f"Error creating order: {response.status_code} {response.text}")
            return None  # or handle error as needed

    request.session['ordered_items_by_shop'] = ordered_items_by_shop
    return unique_invoice_ids  # Return the list of unique invoice IDs


def payment_success(request):
    # Retrieve payment method
    payment_method = request.session.get('payment_method', 'cod')

    # Gather order details from session or other sources as needed
    referrer = request.session.get('referrer')
    shipping_details = request.session.get('shipping_address', {})
    items = request.session.get('ordered_items', [])
    discount_price = request.session.get('total_discount', 0)
    access_token = request.session.get('access_token', '')

    # For Xendit payment, validate the success status from Xendit response
    if payment_method == 'xendit':
        # Assuming this function is accessed only after Xendit payment success
        unique_invoice_ids = create_order(
            request,
            referrer=referrer,
            shipping_details=shipping_details,
            payment_method=payment_method,
            items=items,
            discount_price=discount_price,
            access_token=access_token
        )

    elif payment_method == 'cod':
        # Directly create order without Xendit processing
        unique_invoice_ids = create_order(
            request,
            referrer=referrer,
            shipping_details=shipping_details,
            payment_method=payment_method,
            items=items,
            discount_price=discount_price,
            access_token=access_token
        )

    # Check if order creation was successful
    if unique_invoice_ids:
        return JsonResponse({'status': 'success', 'order_numbers': unique_invoice_ids})
    else:
        return JsonResponse({'status': 'error', 'message': 'Order creation failed'}, status=500)
