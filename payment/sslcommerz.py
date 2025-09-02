import string
import random
from django.conf import settings
from sslcommerz_lib import SSLCOMMERZ


from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent.parent

from dotenv import load_dotenv
import os

load_dotenv()

load_dotenv(dotenv_path=BASE_DIR / ".env")


SUCCESS_URL = os.getenv("SUCCESS_URL")

FAIL_URL = os.getenv("FAIL_URL")
CANCEL_URL = os.getenv("CANCEL_URL")


def generator_trangection_id( size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


    

def sslcommerz_payment_gateway(request, name, amount,id,token):

    
    cradentials = {'store_id':'techk68ad6d2c28c8b',
            'store_pass':"techk68ad6d2c28c8b@ssl", 'issandbox': True} 
            
    sslcommez = SSLCOMMERZ(cradentials)
    body = {}
    body['total_amount'] = amount
    body['currency'] = "BDT"
    body['tran_id'] = generator_trangection_id()
    body['success_url'] = f'{SUCCESS_URL}{id}/?token={token}'
    body['fail_url'] = f'{FAIL_URL}'
    body['cancel_url'] = f'{CANCEL_URL}'
    body['emi_option'] = 0
    body['cus_name'] = name
    body['cus_email'] = 'request.data["email"]'
    body['cus_phone'] = 'request.data["phone"]'
    body['cus_add1'] = 'request.data["address"]'
    body['cus_city'] = 'request.data["address"]'
    body['cus_country'] = 'Bangladesh'
    body['shipping_method'] = "NO"
    body['multi_card_name'] = ""
    body['num_of_item'] = 1
    body['product_name'] = "Shiping Free"
    body['product_category'] = "Pay"
    body['product_profile'] = "general"
    body['value_a'] = name

    response = sslcommez.createSession(body)
    return 'https://sandbox.sslcommerz.com/gwprocess/v4/gw.php?Q=pay&SESSIONKEY=' + response["sessionkey"]