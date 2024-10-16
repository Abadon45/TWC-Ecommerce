import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse


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


def create_xendit_invoice(
        customer_name, customer_email, customer_phone,
        items, shipping_amount, unique_invoice_id,
        success_redirect_url, failure_redirect_url, shop_count):
    # Xendit API URL for creating an invoice
    xendit_url = "https://api.xendit.co/v2/invoices"

    # Calculate total amount from items
    total_amount = sum(item["quantity"] * item["price"] for item in items)

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
        "payer_name": customer_name,  # Customer name
        "payer_phone": customer_phone  # Customer phone number
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
