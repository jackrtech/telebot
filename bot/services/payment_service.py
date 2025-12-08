"""
Stripe payment integration service
"""
import stripe
import json

def create_payment_session(order_data, stripe_secret_key, success_url, cancel_url):
    """Create a Stripe checkout session for an order"""
    stripe.api_key = stripe_secret_key
    
    # Build line items from order
    line_items = []
    for item, details in order_data['items'].items():
        line_items.append({
            'price_data': {
                'currency': order_data['currency'].lower(),
                'product_data': {
                    'name': item,
                },
                'unit_amount': int(details['price'] * 100),  # Convert to cents
            },
            'quantity': details['quantity'],
        })
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'order_id': order_data['order_id'],
            'user_id': str(order_data['user_id']),
            'username': order_data.get('username', 'Unknown'),
            'customer_name': order_data['name'],
            'address_line1': order_data['address_line1'],
            'city': order_data['city'],
            'postcode': order_data['postcode'],
            'items': json.dumps(order_data['items']),
            'total': str(order_data['total'])
        }
    )
    
    return session
