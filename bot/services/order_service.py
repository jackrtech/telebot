"""
Order management and ID generation service
"""
import csv
import os
from datetime import datetime
import pytz

ORDERS_FILE = 'orders.csv'
UK_TZ = pytz.timezone('Europe/London')

def generate_order_id():
    """Generate unique order ID based on timestamp"""
    now = datetime.now(UK_TZ)
    return f"ORD{now.strftime('%Y%m%d%H%M%S')}"

def save_order_to_csv(order_data):
    """Save order to CSV file"""
    file_exists = os.path.isfile(ORDERS_FILE)
    
    with open(ORDERS_FILE, 'a', newline='', encoding='utf-8') as f:
        fieldnames = [
            'order_id', 'timestamp', 'name',
            'address_line1', 'city', 'postcode',
            'items', 'total', 'payment_status'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        # Format items as string
        items_str = "; ".join([
            f"{item} x{details['quantity']}"
            for item, details in order_data['items'].items()
        ])
        
        writer.writerow({
            'order_id': order_data['order_id'],
            'timestamp': order_data['timestamp'],
            'name': order_data['name'],
            'address_line1': order_data['address_line1'],
            'city': order_data['city'],
            'postcode': order_data['postcode'],
            'items': items_str,
            'total': order_data['total'],
            'payment_status': order_data.get('payment_status', 'pending')
        })

def create_order(user_id, customer_info, cart, products_flat, currency='GBP'):
    """Create a new order from cart and customer info"""
    order_id = generate_order_id()
    timestamp = datetime.now(UK_TZ).strftime('%Y-%m-%d %H:%M:%S')
    
    # Build items dictionary with prices
    items = {}
    total = 0.0
    for item, quantity in cart.items():
        price = float(products_flat.get(item, 0))
        items[item] = {
            'quantity': quantity,
            'price': price
        }
        total += price * quantity
    
    order_data = {
        'order_id': order_id,
        'timestamp': timestamp,
        'user_id': user_id,
        'name': customer_info['name'],
        'address_line1': customer_info['address_line1'],
        'city': customer_info['city'],
        'postcode': customer_info['postcode'],
        'items': items,
        'total': round(total, 2),
        'currency': currency,
        'payment_status': 'pending'
    }
    
    # Save to CSV
    save_order_to_csv(order_data)
    
    return order_data
