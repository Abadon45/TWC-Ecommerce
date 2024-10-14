import requests
from django.conf import settings
from django.http import JsonResponse

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
        "ncr": {(0, 2): 100.00, (3, 4): 120.00, (5, 6): 160.00, (7, 8): 180.00, (9, 15): 300.00, (16, 20): 420.00, (20, 27): 580.00},
        "luzon": {(0, 2): 160.00, (3, 4): 180.00, (5, 6): 240.00, (7, 8): 260.00, (9, 15): 380.00, (16, 20): 500.00, (20, 27): 660.00},
        "visayas": {(0, 2): 180.00, (3, 4): 200.00, (5, 6): 260.00, (7, 8): 280.00, (9, 15): 400.00, (16, 20): 520.00, (20, 27): 680.00},
        "mindanao": {(0, 2): 200.00, (3, 4): 220.00, (5, 6): 280.00, (7, 8): 300.00, (9, 15): 420.00, (16, 20): 540.00, (20, 27): 700.00}
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
