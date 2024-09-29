import requests

def create_payment():
    # Your API key
    api_key = "ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2T1RjME16QXhMQ0p1WVcxbElqb2lNVGN5TVRRNU5EYzROaTQwT0RjeU5qWWlmUS5aY1pMNUNVWTdSRld1S3d6eEhwLXlOS3F0RWUxVEhyZmh5TTdyWmplc1pGU3FjZVZWalptZWRudEZSdHh1MEk1M29sQWZIQkd6dVRLT3lvUWpjTEo5dw=="

    # Step 1: Get the API token
    token_response = requests.post(
        url="https://accept.paymob.com/api/auth/tokens",
        json={"api_key": api_key}
    )

    if token_response.status_code != 200:
        print("Failed to get token.")
        return

    api_token = token_response.json().get("token")
    
    if not api_token:
        print("No token received.")
        return

    # Step 2: Create the order
    payload = {
        "auth_token": api_token,
        "delivery_needed": "false",
        "amount_cents": 100,
        "currency": "EGP",
        "items": [
            {
                "name": "Fake Product 1",
                "amount_cents": "500000",
                "description": "A fake product description.",
                "quantity": "1"
            },
            {
                "name": "Fake Product 2",
                "amount_cents": "200000",
                "description": "Another fake product.",
                "quantity": "1"
            }
        ],
        "shipping_data": {},
        "shipping_details": {}
    }

    order_response = requests.post(
        url="https://accept.paymob.com/api/ecommerce/orders",
        json=payload
    )

    if order_response.status_code != 200:
        print("Failed to create order.")
        return

    order_id = order_response.json().get('id')

    if not order_id:
        print("No order ID received.")
        return

    # Step 3: Generate payment key
    payment_key_payload = {
        "auth_token": api_token,
        "amount_cents": "100",
        "expiration": 3600,
        "order_id": str(order_id),
        "billing_data": {
            "apartment": "803",
            "email": "fakeemail@test.com",
            "floor": "42",
            "first_name": "John",
            "street": "Fake Street",
            "building": "1234",
            "phone_number": "+201064160586",
            "shipping_method": "PKG",
            "postal_code": "12345",
            "city": "FakeCity",
            "country": "EG",
            "last_name": "Doe",
            "state": "FakeState"
        },
        "currency": "EGP",
        "integration_id": 4567561  # Replace with actual integration ID
    }

    payment_key_response = requests.post(
        url="https://accept.paymob.com/api/acceptance/payment_keys",
        json=payment_key_payload
    )

    payment_key_response.raise_for_status()

    payment_key_data = payment_key_response.json().get('token')
    if not payment_key_data:
        raise ValueError("Payment key token is missing in the response")

    # Step 4: Generate iframe link
    link = f"https://accept.paymob.com/api/acceptance/iframes/843753?payment_token={payment_key_data}"
    
    # Returning the link for further use (like rendering it on a webpage or redirecting)
    return link

# Run the payment function
iframe_link = create_payment()
if iframe_link:
    print(f"Payment iframe link: {iframe_link}")
