# utils.py

def fulfiller(region=None):
    
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
        fulfiller = "ncr"
    elif region in luzon:
        fulfiller = "sante valenzuela"
    elif region in visayas:
        fulfiller = "sante valenzuela"
    elif region in mindanao:
        fulfiller = "sante cdo"
    else:
        fulfiller = None

    return fulfiller

