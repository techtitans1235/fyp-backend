from django.http import JsonResponse
from datetime import datetime, timedelta
import hmac
import hashlib
from django.views.decorators.csrf import csrf_exempt

# Constants
JAZZCASH_MERCHANT_ID = ""
JAZZCASH_PASSWORD = ""
JAZZCASH_RETURN_URL = "http://127.0.0.1:8000/success"
JAZZCASH_INTEGRITY_SALT = ""

# Exchange rate
USD_TO_PKR_RATE = 280  # Example exchange rate (1 USD = 280 PKR)

# Define pricing in USD
PRICING_PLANS_USD = {
    "basic": 29.00,   # Amount in USD
    "standard": 99.00,
    "premium": 499.00
}

def checkout(request):
    # Get the plan from the query parameters
    plan = request.GET.get("plan", "").lower()

    # Check if the plan exists in PRICING_PLANS_USD
    if plan not in PRICING_PLANS_USD:
        return JsonResponse({"error": "Invalid pricing plan"}, status=400)

    # Get pricing in USD and convert to PKR
    product_price_usd = PRICING_PLANS_USD[plan]
    product_price_pkr = round(product_price_usd * USD_TO_PKR_RATE, 2)  # Round to 2 decimal places
    product_price_paisa = int(product_price_pkr * 100)  # Convert to paisa for JazzCash

    product_name = f"Subscribe ({plan.capitalize()} Plan)"

    current_datetime = datetime.now()
    pp_TxnDateTime = current_datetime.strftime('%Y%m%d%H%M%S')

    expiry_datetime = current_datetime + timedelta(hours=1)
    pp_TxnExpiryDateTime = expiry_datetime.strftime('%Y%m%d%H%M%S')

    pp_TxnRefNo = "T" + pp_TxnDateTime
    post_data = {
        "pp_Version": "1.0",
        "pp_TxnType": "",
        "pp_Language": "EN",
        "pp_MerchantID": JAZZCASH_MERCHANT_ID,
        "pp_SubMerchantID": "",
        "pp_Password": JAZZCASH_PASSWORD,
        "pp_BankID": "TBANK",
        "pp_ProductID": "RETL",
        "pp_TxnRefNo": pp_TxnRefNo,
        "pp_Amount": product_price_pkr,
        "pp_TxnCurrency": "PKR",
        "pp_TxnDateTime": pp_TxnDateTime,
        "pp_BillReference": "billRef",
        "pp_Description": f"{plan.capitalize()} plan subscription",
        "pp_TxnExpiryDateTime": pp_TxnExpiryDateTime,
        "pp_ReturnURL": JAZZCASH_RETURN_URL,
        "pp_SecureHash": "",
        "ppmpf_1": "1",
        "ppmpf_2": "2",
        "ppmpf_3": "3",
        "ppmpf_4": "4",
        "ppmpf_5": "5"
    }

    # Generate Secure Hash
    sorted_string = "&".join(f"{key}={value}" for key, value in sorted(post_data.items()) if value != "")
    pp_SecureHash = hmac.new(
        JAZZCASH_INTEGRITY_SALT.encode(),
        sorted_string.encode(),
        hashlib.sha256
    ).hexdigest()
    post_data['pp_SecureHash'] = pp_SecureHash

    # Return JSON response
    response_data = {
        "product_name": product_name,
        # "product_price_usd": product_price_usd,  # Price in USD for reference
        "product_price": product_price_pkr,  # Price in PKR for display
        "post_data": post_data
    }
    return JsonResponse(response_data)

@csrf_exempt
def success(request):
    return JsonResponse({"message": "Payment Successful!"})
