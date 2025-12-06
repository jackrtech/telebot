"""
Text and message formatting utilities
"""

def format_price(price, currency='GBP'):
    """Format price with currency symbol"""
    symbols = {
        'GBP': '£',
        'USD': '$',
        'EUR': '€'
    }
    symbol = symbols.get(currency, currency)
    return f"{symbol}{price}"

def format_cart_message(cart, products_flat, currency='GBP'):
    """Format cart contents into a readable message"""
    if not cart:
        return "Your cart is empty."
    
    lines = ["🛒 Your Cart:\n"]
    total = 0.0
    
    for item, quantity in cart.items():
        price = float(products_flat.get(item, 0))
        subtotal = price * quantity
        total += subtotal
        lines.append(f"{item} x{quantity} - {format_price(subtotal, currency)}")
    
    lines.append(f"\nTotal: {format_price(total, currency)}")
    return "\n".join(lines)

def format_order_summary_individual(cart, products_flat, customer_info, currency='GBP'):
    """Format order summary with items listed individually"""
    lines = [
        "📋 Order Summary\n",
        "Items:"
    ]
    
    total = 0.0
    for item, quantity in cart.items():
        price = float(products_flat.get(item, 0))
        # List each item individually
        for _ in range(quantity):
            lines.append(f"• {item}")
        total += price * quantity
    
    lines.extend([
        f"\nTotal: {format_price(total, currency)}",
        "\nDelivery Address:",
        customer_info['name'],
        customer_info['address_line1'],
        customer_info['city'],
        customer_info['postcode']
    ])
    
    return "\n".join(lines)

def format_order_summary(order_data, currency='GBP'):
    """Format order summary for emails and messages"""
    lines = [
        f"Order ID: {order_data['order_id']}",
        f"\nCustomer Details:",
        f"Name: {order_data['name']}",
    ]
    
    
    lines.extend([
        f"\nDelivery Address:",
        f"{order_data['address_line1']}",
        order_data['city'],
        order_data['postcode'],
        f"\nItems:"
    ])
    
    total = 0.0
    for item, details in order_data['items'].items():
        quantity = details['quantity']
        price = details['price']
        subtotal = quantity * price
        total += subtotal
        for _ in range(quantity):
            lines.append(f"• {item}")
    
    lines.append(f"\nTotal: {format_price(total, currency)}")
    
    return "\n".join(lines)
