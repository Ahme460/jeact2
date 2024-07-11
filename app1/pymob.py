import requests as re
import random
import string
from .models import CartModel, Customer_user, CartItem

def generate_random_phone_number():
    prefix = "+2010"
    suffix = ''.join(random.choices(string.digits, k=8))
    return prefix + suffix

def generate_random_name():
    first_names = ["Ahmed", "Mohamed", "Ali", "Hassan", "Omar", "Youssef", "Mahmoud", "Mostafa"]
    last_names = ["Ahmed", "Ali", "Hassan", "Youssef", "Salem", "Ibrahim", "Nassar", "Fahmy"]
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    return last_name

def pay(api_: str, total_price, user):
    cart = CartModel.objects.get(customer=user)
    cart_items = CartItem.objects.filter(cart=cart)
    currency = Customer_user.objects.get(email=user.email).currency
    email = user.email
    first_name = user.first_name
    last_name=generate_random_name()
    
    items = []
    for item in cart_items:
        items.append({
            "name": item.product.name,
            "amount_cents": int(item.product.price * 100),  # تحويل السعر إلى سنت
            "description": item.product.about_product,
            "quantity": item.quantity
        })

    total_amount_cents = int(total_price * 100)
    api = api_
    
    token_response = re.post(
        url="https://accept.paymob.com/api/auth/tokens",
        json={"api_key": api}
    )
    api_token = token_response.json().get("token", None)
    
    order_payload = {
        "auth_token": api_token,
        "delivery_needed": "true",
        "amount_cents": total_amount_cents,
        "currency": currency,
        "items": items,
        "shipping_data": {},
        "shipping_details": {}
    }
    
    order_response = re.post(
        url="https://accept.paymob.com/api/ecommerce/orders",
        json=order_payload
    )
    
    order_id = order_response.json().get('id', None)
    
    payment_key_payload = {
        "auth_token": api_token,
        "amount_cents": total_amount_cents,
        "expiration": 3600,
        "order_id": str(order_id),
        "billing_data": {
            "apartment": "",
            "email": email,
            "floor": "",
            "first_name": first_name,
            "street": "",
            "building": "",
            "phone_number": generate_random_phone_number(),
            "shipping_method": "",
            "postal_code": "",
            "city": "",
            "country": "",
            "last_name": last_name,
            "state": ""
        },
        "currency": currency,
        "integration_id": 4603869  # هذا معرف التكامل الخاص بك من حساب باي موب
    }
    
    payment_key_response = re.post(
        url="https://accept.paymob.com/api/acceptance/payment_keys",
        json=payment_key_payload
    )
    
    payment_token = payment_key_response.json().get('token', None)
    
    payment_url = f"https://accept.paymob.com/api/acceptance/iframes/854152?payment_token={payment_token}"
    
    return payment_url
