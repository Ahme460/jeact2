import requests as re
import random
import string
from .models import CartModel, Customer_user, CartItem
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

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

def pay(api_key: str, total_price, user):
    try:
        # Retrieve the user's cart and cart items
        cart = CartModel.objects.get(customer=user)
        cart_items = CartItem.objects.filter(cart=cart)
        
        # Get user details
        customer_user = Customer_user.objects.get(email=user.email)
        currency = customer_user.currence
        email = user.email
        first_name = user.first_name
        last_name = generate_random_name()
        print(first_name)
        
        # Prepare items for the payment request
        items = []
        for item in cart_items:
            items.append({
                "name": item.product.name,
                "amount_cents": int(item.product.price * 100),  # Convert price to cents
                "description": item.product.about_product,
                "quantity": item.quantity
            })
            
        print(items)
       

        # Calculate total amount in cents
        total_amount_cents = int(total_price * 100)
        
        # API endpoint for token generation
        url = "https://accept.paymob.com/api/auth/tokens"
        
        # Make the request to get the API token
        token_response = re.post(url, json={"api_key": api_key})
        token_response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        
        #token_data = token_response.json()
        #api_token = token_data.get("token")
        api_token = token_response.json().get("token", None)
        if not api_token:
            raise ValueError("API token is missing in the response")
        
        print(type(str(int(total_amount_cents)*100)))
        print("Token Response:", api_token)  # Debugging statement

        # Create the order
        order_url = "https://accept.paymob.com/api/ecommerce/orders"
        order_payload = {
            "auth_token": api_token,
            "delivery_needed": False,
            "amount_cents": str(total_amount_cents),
            "currency": currency,
            #"merchant_order_id": str(cart.id),
            "items": items
        }
        print("beeee")
        order_response = re.post(order_url, json=order_payload)
        order_response.raise_for_status()
        print(order_response.raise_for_status)
        
        #print("Order Response:", order_data)  # Debugging statement

        order_id =order_response.json().get('id', None)
        print("_____")
        print(order_id)
        print(generate_random_phone_number())
        print(type(generate_random_phone_number()))
        # Generate a payment key
        
        payment_key_url = "https://accept.paymob.com/api/acceptance/payment_keys"
        billing_data = {
            "apartment": "NA",
            "email": "ahmeoon1234@gmail.com",
            "floor": "NA",
            "first_name": "ajeee",
            "street": "NA",
            "building": "NA",
            "phone_number": "+201234575432",#generate_random_phone_number(),
            "shipping_method": "NA",
            "postal_code": "NA",
            "city": "NA",
            "country": "NA",
            "last_name": last_name,
            "state": "NA"
        }
        payment_key_payload = {
            "auth_token": api_token,
            "amount_cents": str(total_amount_cents),
            "expiration": 3600,  # 1 hour expiration
            "order_id": order_id,
            "billing_data": billing_data,
            "currency": currency,
            #"integration_id": 4603869
            #"integration_id": 4603869
           # # Replace with actual integration ID
           "integration_id": 4567561
        }
       # print("Payment Key Payload:", payment_key_payload)  # Debugging statement
        
        payment_key_response = re.post(payment_key_url, json=payment_key_payload)
        payment_key_response.raise_for_status()
        #payment_key_data = payment_key_response.json()
        payment_key_data =payment_key_response.json().get('token', None)
        print("Payment Key Response:", payment_key_data)  # Debugging statement
        print("i,m here")
        link = f"https://accept.paymob.com/api/acceptance/iframes/843753?payment_token={payment_key_data}"
        return link

    except re.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}") 
    # Log HTTP errors
        if order_response is not None:
            print(f"Order Response Text: {order_response.text}")
    except Exception as err:
    
        print(f"An error occurred: {err}")  # Log other errors